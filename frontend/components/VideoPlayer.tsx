"use client";

import { useRef, useState, useEffect } from "react";

interface Prediction {
  action_id: number;
  action_name: string;
  confidence: number;
}

interface PredictionResult {
  top_prediction: Prediction;
  top5_predictions: Prediction[];
  timestamp?: number;
  segment?: string;
}

interface ContinuousPredictions {
  video_duration: number;
  num_predictions: number;
  predictions: PredictionResult[];
}

interface Props {
  videoFile: File;
  prediction: ContinuousPredictions | PredictionResult;
}

// this object contains descriptions for each ballet action
const actionDescriptions: { [key: string]: string } = {
  Pirouette: "Spinning turn on one foot",
  "Grand Jeté": "Large leap through the air",
  Arabesque: "Standing on one leg, other leg extended back",
  Fouetté: "Whipping turn with leg movement",
  "Pas de Bourrée": "Quick, small connecting steps",
  "Balancing Extension": "Extended leg balance pose",
  Attitude: "Bent leg raised behind or in front",
  "Chaîné Turn": "Series of quick spinning turns",
  "Extension Second": "Leg extended to the side",
  "Waltz Step": "Flowing waltz-like movement",
  Cabriolé: "Jump with legs beating together",
};

export default function VideoPlayer({ videoFile, prediction }: Props) {
  // this component shows the video and predictions
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // check if we have continuous predictions or just one prediction
  const isContinuous = "predictions" in prediction;
  const predictions = isContinuous
    ? (prediction as ContinuousPredictions).predictions
    : [prediction as PredictionResult];

  const [displayedPrediction, setDisplayedPrediction] = useState(
    predictions[0].top_prediction
  );
  const [currentSegment, setCurrentSegment] = useState(0);

  // create video URL when component loads
  useEffect(() => {
    const url = URL.createObjectURL(videoFile);
    setVideoUrl(url);

    // cleanup URL when component is removed
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [videoFile]);

  // update current time and prediction as video plays
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      setCurrentTime(time);

      // find which prediction segment we are in (every 10 seconds)
      const segmentIndex = Math.floor(time / 10);

      if (
        segmentIndex < predictions.length &&
        segmentIndex !== currentSegment
      ) {
        // update to new prediction for this time segment
        setDisplayedPrediction(predictions[segmentIndex].top_prediction);
        setCurrentSegment(segmentIndex);
        console.log(
          `Updated prediction at ${time.toFixed(1)}s: ${
            predictions[segmentIndex].top_prediction.action_name
          }`
        );
      }
    }
  };

  // get video duration when video loads
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch((error) => {
          console.error("Error playing video:", error);
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        Video & Prediction
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Player */}
        <div className="space-y-4">
          <div className="relative bg-black rounded-xl overflow-hidden">
            <video
              ref={videoRef}
              src={videoUrl}
              className="w-full h-auto"
              controls
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onError={(e) => console.error("Video error:", e)}
            >
              Your browser does not support the video tag.
            </video>
          </div>

          {/* Video Timeline Info */}
          <div className="bg-gray-100 rounded-lg p-3">
            <div className="flex justify-between text-sm text-gray-600">
              <span>
                {Math.floor(currentTime)}s / {Math.floor(duration)}s
              </span>
              <span>{isPlaying ? "Playing" : "Paused"}</span>
            </div>
          </div>

          {/* Video Controls */}
          <button
            onClick={handlePlayPause}
            className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 shadow-lg"
          >
            {isPlaying ? "Pause" : "Play"}
          </button>

          <p className="text-sm text-gray-500 text-center">{videoFile.name}</p>
        </div>

        {/* Prediction Display */}
        <div className="space-y-4">
          {/* this shows the top prediction and updates as video plays */}
          <div className="bg-purple-600 rounded-xl shadow-lg p-6 text-white">
            <h3 className="text-lg font-semibold mb-2">
              Predicted Next Action
            </h3>
            <p className="text-4xl font-bold mb-2">
              {displayedPrediction.action_name}
            </p>
            <p className="text-base opacity-90 italic mb-2">
              {actionDescriptions[displayedPrediction.action_name] ||
                "Ballet movement"}
            </p>
            <p className="text-lg opacity-90">
              Confidence: {displayedPrediction.confidence.toFixed(2)}
            </p>
            {isPlaying && (
              <div className="mt-3 flex items-center gap-2 text-sm bg-white/20 rounded-lg px-3 py-2">
                <span>
                  Watch for:{" "}
                  {actionDescriptions[displayedPrediction.action_name]}
                </span>
              </div>
            )}
            {currentSegment > 0 && (
              <div className="mt-2 text-xs opacity-75">
                Analyzing segment {currentSegment + 1} of {predictions.length}
              </div>
            )}
          </div>

          <div className="bg-gray-50 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">
              Top 5 Predictions
            </h3>
            <div className="space-y-3">
              {predictions[currentSegment]?.top5_predictions
                .slice(0, 5)
                .map((prediction, index) => (
                  <div
                    key={prediction.action_id}
                    className="flex items-center gap-3"
                  >
                    <span className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-semibold text-sm">
                      {index + 1}
                    </span>
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-gray-800">
                          {prediction.action_name}
                        </span>
                        <span className="text-sm text-gray-600">
                          {prediction.confidence.toFixed(2)}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            index === 0
                              ? "bg-purple-600"
                              : index === 1
                              ? "bg-blue-400"
                              : index === 2
                              ? "bg-cyan-400"
                              : index === 3
                              ? "bg-teal-400"
                              : index === 4
                              ? "bg-green-400"
                              : index === 5
                              ? "bg-green-200"
                              : "bg-green-400"
                          }`}
                          style={{
                            width: `${
                              (prediction.confidence /
                                predictions[currentSegment].top5_predictions[0]
                                  .confidence) *
                              100
                            }%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* this shows what to watch for in the video */}
          <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-4">
            <p className="text-sm font-bold text-yellow-900 mb-2">
              What to Look For:
            </p>
            <p className="text-sm text-yellow-800 mb-2">
              The model predicts you'll see:{" "}
              <strong>
                {actionDescriptions[displayedPrediction.action_name]}
              </strong>
            </p>
            <p className="text-xs text-yellow-700">
              Prediction updates every 10 seconds as video plays!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
