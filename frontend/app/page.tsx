"use client";

import { useState } from "react";
import ModelInfo from "@/components/ModelInfo";
import VideoUpload from "@/components/VideoUpload";
import VideoPlayer from "@/components/VideoPlayer";

const API_URL = "http://localhost:8001";

interface Prediction {
  action_id: number;
  action_name: string;
  confidence: number;
}

interface PredictionResult {
  top_prediction: Prediction;
  top5_predictions: Prediction[];
  all_predictions: number[];
  model_info: {
    accuracy: number;
    input_shape: number[];
    num_classes: number;
  };
}

export default function Home() {
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [uploadedVideoFile, setUploadedVideoFile] = useState<File | null>(null);

  // this function handles the prediction from video upload
  const handlePredictionFromVideo = (
    prediction: PredictionResult, // this is the prediction from the video
    videoFile: File // this is the video file
  ) => {
    setPrediction(prediction); // this sets the prediction
    setUploadedVideoFile(videoFile); // this sets the video file
  };

  return (
    <main className="min-h-screen bg-indigo-50">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            Ballet Action Anticipation
          </h1>
          <p className="text-xl text-gray-600">
            Prediction of next ballet movements - Using GRU and Transformer
            neural networks trained on AnnChor dataset
          </p>
        </div>

        <ModelInfo />

        <div className="max-w-4xl mx-auto">
          <VideoUpload
            onPredictFromVideo={handlePredictionFromVideo}
            loading={loading}
            onVideoSelect={setSelectedVideo}
            setLoading={setLoading}
            setError={setError}
          />

          {error && (
            <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
              {error}
            </div>
          )}

          {/* this displays the video player with prediction */}
          {prediction && uploadedVideoFile && (
            <VideoPlayer
              videoFile={uploadedVideoFile}
              prediction={prediction}
            />
          )}

          <div className="bg-white rounded-2xl shadow-xl p-8 mt-8">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              How to Use
            </h2>
            <div className="space-y-4 text-gray-600">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold mr-3">
                  1
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    Upload a Ballet Video
                  </h3>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold mr-3">
                  2
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    Model Processing
                  </h3>
                  <p>
                    Backend extracts I3D features and the model processes the
                    video to understand movement patterns and predict the next
                    action.
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-semibold mr-3">
                  3
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    View Results
                  </h3>
                  <p>
                    See the predicted next action with confidence scores and top
                    5 alternative predictions.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>
            Built with Next.js, FastAPI, and ONNX Runtime. Model trained on
            AnnChor dataset (1020 videos, 11 action classes)
          </p>
        </div>
      </div>
    </main>
  );
}
