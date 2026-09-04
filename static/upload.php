<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = $_POST['title'];
    $desc = $_POST['desc'];
    $icon = $_POST['icon'] ?? '🎥';

    // Ensure the uploads directory exists
    $targetDir = "uploads/";
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0777, true); // Create the directory if it doesn't exist
    }

    // Save uploaded file
    $fileName = basename($_FILES["video"]["name"]);
    $targetPath = $targetDir . $fileName;

    // Validate file type (optional but recommended)
    $allowedTypes = ['video/mp4', 'video/mkv', 'video/webm'];
    if (!in_array($_FILES["video"]["type"], $allowedTypes)) {
        echo "Invalid file type. Only MP4, MKV, and WebM are allowed.";
        exit;
    }

    if (move_uploaded_file($_FILES["video"]["tmp_name"], $targetPath)) {
        // Append to tutorials.json
        $dataFile = 'data/tutorials.json';
        if (file_exists($dataFile)) {
            $tutorials = json_decode(file_get_contents($dataFile), true);
        } else {
            $tutorials = []; // Initialize an empty array if the file doesn't exist
        }

        $tutorials[] = [
            "title" => $title,
            "description" => $desc,
            "icon" => $icon,
            "videoPath" => $targetPath
        ];

        // Save the updated tutorials array back to the JSON file
        if (file_put_contents($dataFile, json_encode($tutorials, JSON_PRETTY_PRINT))) {
            echo "Success";
        } else {
            echo "Failed to update tutorial data.";
        }
    } else {
        echo "Upload failed";
    }
}
?>
