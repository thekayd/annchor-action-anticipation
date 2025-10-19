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

interface Props {
  prediction: PredictionResult;
  videoName?: string | null;
}

export default function PredictionDisplay({ prediction, videoName }: Props) {
  const { top_prediction, top5_predictions } = prediction;

  // this gets the max confidence for scaling
  const maxConfidence = Math.max(...top5_predictions.map((p) => p.confidence));

  return (
    <div className="space-y-6 mb-8">
      {/* this shows the top prediction */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
        <h2 className="text-2xl font-semibold mb-2">Predicted Next Action</h2>
        {videoName && (
          <p className="text-sm opacity-90 mb-4">Video Name: {videoName}</p>
        )}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-5xl font-bold">{top_prediction.action_name}</p>
            <p className="text-xl mt-2 opacity-90">
              ID: {top_prediction.action_id}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-75">Confidence</p>
            <p className="text-4xl font-bold">
              {top_prediction.confidence.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* this shows the top 5 predictions */}
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <h3 className="text-2xl font-semibold text-gray-800 mb-6">
          Top 5 Predictions
        </h3>
        <div className="space-y-4">
          {top5_predictions.map((prediction, index) => (
            <div key={prediction.action_id}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <span className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 font-semibold text-sm">
                    {index + 1}
                  </span>
                  <span className="font-medium text-gray-800">
                    {prediction.action_name}
                  </span>
                </div>
                <span className="text-gray-600 font-medium">
                  {prediction.confidence.toFixed(2)}
                </span>
              </div>

              {/* this shows the progress bar for the prediction */}
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
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
                      ? "bg-green-400"
                      : "bg-green-400"
                  }`}
                  style={{
                    width: `${(prediction.confidence / maxConfidence) * 100}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
