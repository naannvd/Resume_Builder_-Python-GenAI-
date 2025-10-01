import React, { useState } from "react";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { ScrollArea } from "./components/ui/scroll-area";

interface ResumeData {
  full_name?: string;
  title?: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  linkedin?: string;
  portfolio?: { platform: string; url: string }[];
  education?: { degree: string; institution: string; start_year: string; end_year: string; description: string }[];
  experience?: { company: string; title: string; start_year: string; end_year: string; description: string[] }[];
  projects?: { project_name: string; start_year: string; end_year: string; description: string[] }[];
  technical_skills?: string[];
  certifications?: string[];
  languages?: string[];
  [key: string]: unknown;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<ResumeData | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Upload failed: ${res.statusText}`);
      }

      const data = await res.json();
      if (data.parsed) {
        setParsedData(data.parsed);
        setPdfUrl(data.pdf_url);
      } else {
        setError("Parsing failed. Please try another resume.");
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen font-sans bg-gradient-to-br from-[#A1CA73] to-[#042F40] text-[#042F40]">
      {/* Left Side: JSON */}
      <div className="w-2/3 p-4 flex flex-col">
        <Card className="flex-grow bg-black text-green-400">
          <CardHeader>
            <CardTitle className="text-lg">📄 Resume Parser</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2 mb-4">
              <Input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="text-white"
              />
              <Button onClick={handleUpload} disabled={loading}>
                {loading ? "Processing..." : "Upload & Parse"}
              </Button>
            </div>

            {error && <p className="text-red-500">❌ {error}</p>}

            <h2 className="text-white font-bold mb-2">Raw Parsed Data</h2>
            <ScrollArea className="h-[70vh] rounded bg-black p-2 border border-green-500">
              {parsedData ? (
                <pre className="text-green-400 whitespace-pre-wrap">
                  {JSON.stringify(parsedData, null, 2)}
                </pre>
              ) : (
                <p className="text-gray-400">No resume parsed yet.</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Right Side: PDF Preview */}
      <div className="w-1/3 border-l border-gray-300 flex flex-col">
        <Card className="flex-grow">
          <CardHeader>
            <CardTitle className="text-lg">📑 Resume Preview</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow">
            {pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-[70vh] border rounded"
                title="Resume Preview"
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No preview available
              </div>
            )}
            {pdfUrl && (
              <a
                href={pdfUrl}
                download
                className="mt-4 inline-block w-full text-center bg-[#042F40] text-white py-2 rounded hover:bg-[#064d66] transition"
              >
                ⬇ Download PDF
              </a>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default App;
