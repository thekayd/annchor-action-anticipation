"use client";

import { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:8001";

interface ModelInfoData {
  class_names: string[];
  input_shape: number[];
  num_classes: number;
  accuracy: number;
  model_path: string;
}

export default function ModelInfo() {
  // this component shows information about the model
  const [info, setInfo] = useState<ModelInfoData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // this function gets the model information from the API
    const fetchModelInfo = async () => {
      try {
        const response = await axios.get(`${API_URL}/model-info`);
        setInfo(response.data);
      } catch (error) {
        console.error("Failed to fetch model info:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchModelInfo();
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto mb-8 bg-white rounded-2xl shadow-xl p-8">
        <p className="text-gray-500 text-center">
          Loading model information...
        </p>
      </div>
    );
  }

  if (!info) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto mb-8 bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        Model Information
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* this shows the model accuracy */}
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6">
          <div className="text-sm font-medium text-indigo-600 mb-1">
            Model Accuracy
          </div>
          <div className="text-3xl font-bold text-gray-800">
            {info.accuracy}%
          </div>
          <div className="text-sm text-gray-500 mt-1">On test set</div>
        </div>

        {/* this shows the number of action classes */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6">
          <div className="text-sm font-medium text-blue-600 mb-1">
            Action Classes
          </div>
          <div className="text-3xl font-bold text-gray-800">
            {info.num_classes}
          </div>
          <div className="text-sm text-gray-500 mt-1">Ballet movements</div>
        </div>

        {/* this shows the input shape for the model */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6">
          <div className="text-sm font-medium text-purple-600 mb-1">
            Input Shape
          </div>
          <div className="text-3xl font-bold text-gray-800">
            {info.input_shape[1]}x{info.input_shape[2]}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            Time steps x Features
          </div>
        </div>
      </div>

      {/* this shows all the available action classes */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">
          Available Actions
        </h3>
        <div className="flex flex-wrap gap-2">
          {info.class_names.map((name, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
            >
              {name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
