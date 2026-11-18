import { useEffect, useState } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [progress, setProgress] = useState(0);
  const [thumbnailUrl, setThumbnailUrl] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  function selectFile(event) {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setProgress(0);
    setThumbnailUrl(null);
    setError("");
  }

  async function uploadFile() {
    if (!file) return;
    const data = new FormData();
    data.append("file", file);
    setError("");

    try {
      const response = await axios.post("http://localhost:8000/upload", data, {
        onUploadProgress: (event) => {
          if (event.total) setProgress(Math.round((event.loaded * 100) / event.total));
        },
      });
      setThumbnailUrl(response.data.thumbnail_url);
    } catch (uploadError) {
      setError(uploadError.response?.data?.detail || "Не удалось загрузить файл");
    }
  }

  return (
    <main>
      <input type="file" accept="image/png,image/jpeg" onChange={selectFile} />
      {previewUrl && <img src={previewUrl} alt="Предпросмотр" />}
      <button type="button" onClick={uploadFile} disabled={!file}>Загрузить</button>
      <p>Прогресс: {progress}%</p>
      {error && <p>Ошибка: {error}</p>}
      {thumbnailUrl && <img src={thumbnailUrl} alt="Миниатюра" />}
    </main>
  );
}
