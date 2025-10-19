"use client";

import { useState, useRef, useEffect } from "react";

interface Props {
  onPredictFromVideo: (result: any, videoFile: File) => void;
  loading: boolean;
  onVideoSelect: (name: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export default function VideoUpload({
  onPredictFromVideo,
  loading,
  onVideoSelect,
  setLoading,
  setError,
}: Props) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>("gru");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // this acceots file and modeltype as inputs to process video with selected model
  const processVideoWithModel = async (file: File, modelType: string) => {
    setLoading(true);
    setError(null);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `http://localhost:8001/predict-continuous?model_type=${modelType}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to process video");
      }

      const result = await response.json();
      onPredictFromVideo(result, file);
    } catch (error: any) {
      const errorMsg = error.message || "Failed to process video";
      setUploadError(errorMsg);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  // This useeffect allows for re processing the video when model changes
  useEffect(() => {
    if (uploadedFile && !loading) {
      processVideoWithModel(uploadedFile, selectedModel);
    }
  }, [selectedModel]); // the selected model then only re-runs when selectedModel changes

  // this handles the video file upload
  const handleVideoUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadError(null);

    // checks the file extensions for validation
    const allowedTypes = [".mp4", ".avi", ".mov", ".mkv", ".webm"];
    const fileExt = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    if (!allowedTypes.includes(fileExt)) {
      setUploadError(`Please upload a video file (${allowedTypes.join(", ")})`);
      return;
    }

    setUploadedFile(file);
    onVideoSelect(file.name);

    // processes the video with the currently selected model
    await processVideoWithModel(file, selectedModel);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        Upload Ballet Video
      </h2>

      <div className="max-w-2xl mx-auto mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Pipeline:
        </label>
        <div className="flex gap-4">
          <button
            onClick={() => setSelectedModel("gru")}
            disabled={loading}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              selectedModel === "gru"
                ? "bg-indigo-600 text-white shadow-lg"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            } disabled:opacity-50`}
          >
            Pipeline 1: GRU (65.88%)
          </button>
          <button
            onClick={() => setSelectedModel("transformer")}
            disabled={loading}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              selectedModel === "transformer"
                ? "bg-purple-600 text-white shadow-lg"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            } disabled:opacity-50`}
          >
            Pipeline 2: Transformer (52.57%)
          </button>
        </div>
      </div>

      <div className="max-w-2xl mx-auto">
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 hover:border-indigo-500 transition-colors">
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Choose and Uploada a Ballet Video For Prediction
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              MP4, MOV, AVI, MKV, WebM
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*,.mp4,.avi,.mov,.mkv,.webm"
              onChange={handleVideoUpload}
              className="hidden"
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={loading}
              className="mt-4 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? "Processing..." : "Select Video"}
            </button>

            {uploadedFile && (
              <p className="mt-4 text-sm text-gray-600 font-medium">
                📹 {uploadedFile.name}
              </p>
            )}
          </div>
        </div>
      </div>

      {uploadError && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
          {uploadError}
        </div>
      )}
    </div>
  );
}
