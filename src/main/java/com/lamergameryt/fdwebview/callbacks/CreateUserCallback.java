package com.lamergameryt.fdwebview.callbacks;

import com.lamergameryt.fdwebview.MainView;
import com.lamergameryt.fdwebview.Statics;
import com.lamergameryt.fdwebview.mysql.Models;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.HexFormat;
import org.json.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("unused")
public class CreateUserCallback extends CustomCallback {

    private final Logger logger = LoggerFactory.getLogger(CreateUserCallback.class);

    public CreateUserCallback() {
        super.name = "create_user";
    }

    @Override
    public void executeCallback(JSONArray args) {
        String name = args.getString(0);
        String dobAsStr = args.getString(1);
        String encodedImage = args.getString(2);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        LocalDate dob = LocalDate.parse(dobAsStr, formatter);

        if (dob.isAfter(LocalDate.now())) {
            MainView.getWebView().eval("invalidInput(\"Please select a valid date of birth.\");");
            return;
        }

        File file = parseImage(encodedImage);
        if (file == null) return;

        file.deleteOnExit();
        String hexEncoding = getFaceEncodings(file);
        //noinspection ResultOfMethodCallIgnored
        file.delete();

        if (hexEncoding == null) return;

        byte[] encoding = HexFormat.of().parseHex(hexEncoding);
        Models.User user = MainView.getHandler().createNewUser(name, dob, encoding);
        if (user == null) {
            logger.error("Failed to create new user " + name);
        }

        MainView.getWebView().eval("showSuccess();");
    }

    private File parseImage(String encodedImage) {
        String[] strings = encodedImage.split(",");
        String extension =
            switch (strings[0]) {
                case "data:image/jpeg;base64" -> ".jpeg";
                case "data:image/png;base64" -> ".png";
                default -> ".jpg";
            };

        byte[] data = Base64.getDecoder().decode(strings[1]);
        Path path;
        try {
            path = Files.createTempFile("fdface", extension);
            Files.write(path, data);
            return path.toFile();
        } catch (IOException e) {
            logger.error("Failed to write decoded image data to temporary file.", e);
            return null;
        }
    }

    private String getFaceEncodings(File imageFile) {
        File script = Statics.getFaceMappingScript();
        if (script == null) return null;

        // Requires face_recognition to be installed as a python dependency.
        ProcessBuilder builder = new ProcessBuilder(
            "python",
            script.getAbsolutePath(),
            imageFile.getAbsolutePath()
        );
        builder.redirectErrorStream(true);

        try {
            Process process = builder.start();
            String result = Statics.streamToString(process.getInputStream()).strip();

            process.destroy();
            if (result.isEmpty()) return null; else return result;
        } catch (IOException e) {
            logger.error("Failed to determine face encodings.", e);
            return null;
        }
    }
}
