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
  education?: {
    degree: string;
    institution: string;
    start_year: string;
    end_year: string;
    description: string;
  }[];
  experience?: {
    company: string;
    title: string;
    start_year: string;
    end_year: string;
    description: string[];
  }[];
  projects?: {
    project_name: string;
    start_year: string;
    end_year: string;
    description: string[];
  }[];
  technical_skills?: string[];
  certifications?: string[];
  languages?: string[];
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

      if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);

      const data = await res.json();
      if (data.parsed) {
        setParsedData(data.parsed);
        setPdfUrl(data.pdf_url);
      } else {
        setError("Parsing failed. Please try another resume.");
      }
    } catch (err: unknown) {
      if (err instanceof Error) setError(err.message);
      else setError("An unknown error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleFieldChange = (field: keyof ResumeData, value: unknown) => {
    setParsedData((prev) =>
      prev ? { ...prev, [field]: value } : { [field]: value }
    );
  };

  /** Add / Remove entry handlers */
  const addEducation = () => {
    const updated = parsedData?.education ? [...parsedData.education] : [];
    updated.push({
      degree: "",
      institution: "",
      start_year: "",
      end_year: "",
      description: "",
    });
    handleFieldChange("education", updated);
  };
  const removeEducation = (i: number) => {
    const updated = [...(parsedData?.education || [])];
    updated.splice(i, 1);
    handleFieldChange("education", updated);
  };

  const addExperience = () => {
    const updated = parsedData?.experience ? [...parsedData.experience] : [];
    updated.push({
      company: "",
      title: "",
      start_year: "",
      end_year: "",
      description: [""],
    });
    handleFieldChange("experience", updated);
  };
  const removeExperience = (i: number) => {
    const updated = [...(parsedData?.experience || [])];
    updated.splice(i, 1);
    handleFieldChange("experience", updated);
  };

  const addProject = () => {
    const updated = parsedData?.projects ? [...parsedData.projects] : [];
    updated.push({
      project_name: "",
      start_year: "",
      end_year: "",
      description: [""],
    });
    handleFieldChange("projects", updated);
  };
  const removeProject = (i: number) => {
    const updated = [...(parsedData?.projects || [])];
    updated.splice(i, 1);
    handleFieldChange("projects", updated);
  };

  return (
    <div className="flex h-screen w-screen font-sans bg-gradient-to-br from-[#A1CA73] to-[#042F40] text-[#042F40]">
      {/* Left Side: Editable Form */}
      <div className="w-2/3 p-4 flex flex-col">
        <Card className="flex-grow bg-white text-black">
          <CardHeader>
            <CardTitle className="text-lg">📄 Resume Editor</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2 mb-4">
              <Input type="file" accept="application/pdf" onChange={handleFileChange} />
              <Button onClick={handleUpload} disabled={loading}>
                {loading ? "Processing..." : "Upload & Parse"}
              </Button>
            </div>

            {error && <p className="text-red-500">❌ {error}</p>}

            {parsedData ? (
              <ScrollArea className="h-[70vh] rounded bg-gray-50 p-3 border">
                <div className="space-y-4">
                  {/* Basic Info */}
                  <Input value={parsedData.full_name || ""} onChange={(e) => handleFieldChange("full_name", e.target.value)} placeholder="Full Name" />
                  <Input value={parsedData.title || ""} onChange={(e) => handleFieldChange("title", e.target.value)} placeholder="Title" />
                  <Input value={parsedData.email || ""} onChange={(e) => handleFieldChange("email", e.target.value)} placeholder="Email" />
                  <Input value={parsedData.phone || ""} onChange={(e) => handleFieldChange("phone", e.target.value)} placeholder="Phone" />
                  <Input value={parsedData.location || ""} onChange={(e) => handleFieldChange("location", e.target.value)} placeholder="Location" />
                  <textarea className="w-full p-2 border rounded" rows={4} value={parsedData.summary || ""} onChange={(e) => handleFieldChange("summary", e.target.value)} placeholder="Career Summary" />

                  {/* Education */}
                  <h3 className="font-bold mt-4">Education</h3>
                  {parsedData.education?.map((edu, i) => (
                    <div key={i} className="border p-2 rounded space-y-2">
                      <Input value={edu.degree || ""} onChange={(e) => { const updated = [...parsedData.education!]; updated[i].degree = e.target.value; handleFieldChange("education", updated); }} placeholder="Degree" />
                      <Input value={edu.institution || ""} onChange={(e) => { const updated = [...parsedData.education!]; updated[i].institution = e.target.value; handleFieldChange("education", updated); }} placeholder="Institution" />
                      <div className="flex space-x-2">
                        <Input value={edu.start_year || ""} onChange={(e) => { const updated = [...parsedData.education!]; updated[i].start_year = e.target.value; handleFieldChange("education", updated); }} placeholder="Start Year" />
                        <Input value={edu.end_year || ""} onChange={(e) => { const updated = [...parsedData.education!]; updated[i].end_year = e.target.value; handleFieldChange("education", updated); }} placeholder="End Year" />
                      </div>
                      <textarea className="w-full p-2 border rounded" rows={2} value={edu.description || ""} onChange={(e) => { const updated = [...parsedData.education!]; updated[i].description = e.target.value; handleFieldChange("education", updated); }} placeholder="Description" />
                      <Button variant="destructive" size="sm" onClick={() => removeEducation(i)}>Remove</Button>
                    </div>
                  ))}
                  <Button variant="secondary" size="sm" onClick={addEducation} className="text-white">+ Add Education</Button>

                  {/* Experience */}
                  <h3 className="font-bold mt-4">Experience</h3>
                  {parsedData.experience?.map((exp, i) => (
                    <div key={i} className="border p-2 rounded space-y-2">
                      <Input value={exp.company || ""} onChange={(e) => { const updated = [...parsedData.experience!]; updated[i].company = e.target.value; handleFieldChange("experience", updated); }} placeholder="Company" />
                      <Input value={exp.title || ""} onChange={(e) => { const updated = [...parsedData.experience!]; updated[i].title = e.target.value; handleFieldChange("experience", updated); }} placeholder="Job Title" />
                      <div className="flex space-x-2">
                        <Input value={exp.start_year || ""} onChange={(e) => { const updated = [...parsedData.experience!]; updated[i].start_year = e.target.value; handleFieldChange("experience", updated); }} placeholder="Start Year" />
                        <Input value={exp.end_year || ""} onChange={(e) => { const updated = [...parsedData.experience!]; updated[i].end_year = e.target.value; handleFieldChange("experience", updated); }} placeholder="End Year" />
                      </div>
                      <textarea className="w-full p-2 border rounded" rows={3} value={exp.description.join("\n")} onChange={(e) => { const updated = [...parsedData.experience!]; updated[i].description = e.target.value.split("\n"); handleFieldChange("experience", updated); }} placeholder="One bullet per line" />
                      <Button variant="destructive" size="sm" onClick={() => removeExperience(i)}>Remove</Button>
                    </div>
                  ))}
                  <Button variant="secondary" size="sm" onClick={addExperience} className="text-white">+ Add Experience</Button>

                  {/* Projects */}
                  <h3 className="font-bold mt-4">Projects</h3>
                  {parsedData.projects?.map((proj, i) => (
                    <div key={i} className="border p-2 rounded space-y-2">
                      <Input value={proj.project_name || ""} onChange={(e) => { const updated = [...parsedData.projects!]; updated[i].project_name = e.target.value; handleFieldChange("projects", updated); }} placeholder="Project Name" />
                      <div className="flex space-x-2">
                        <Input value={proj.start_year || ""} onChange={(e) => { const updated = [...parsedData.projects!]; updated[i].start_year = e.target.value; handleFieldChange("projects", updated); }} placeholder="Start Year" />
                        <Input value={proj.end_year || ""} onChange={(e) => { const updated = [...parsedData.projects!]; updated[i].end_year = e.target.value; handleFieldChange("projects", updated); }} placeholder="End Year" />
                      </div>
                      <textarea className="w-full p-2 border rounded" rows={3} value={proj.description.join("\n")} onChange={(e) => { const updated = [...parsedData.projects!]; updated[i].description = e.target.value.split("\n"); handleFieldChange("projects", updated); }} placeholder="One bullet per line" />
                      <Button variant="destructive" size="sm" onClick={() => removeProject(i)}>Remove</Button>
                    </div>
                  ))}
                  <Button variant="secondary" size="sm" onClick={addProject} className="text-white">+ Add Project</Button>

                  {/* Skills, Certifications, Languages */}
                  <h3 className="font-bold mt-4">Technical Skills</h3>
                  <textarea className="w-full p-2 border rounded" rows={2} value={parsedData.technical_skills?.join(", ") || ""} onChange={(e) => handleFieldChange("technical_skills", e.target.value.split(","))} placeholder="Comma-separated skills" />

                  <h3 className="font-bold mt-4">Certifications</h3>
                  <textarea className="w-full p-2 border rounded" rows={2} value={parsedData.certifications?.join(", ") || ""} onChange={(e) => handleFieldChange("certifications", e.target.value.split(","))} placeholder="Comma-separated certifications" />

                  <h3 className="font-bold mt-4">Languages</h3>
                  <textarea className="w-full p-2 border rounded" rows={2} value={parsedData.languages?.join(", ") || ""} onChange={(e) => handleFieldChange("languages", e.target.value.split(","))} placeholder="Comma-separated languages" />
                </div>
              </ScrollArea>
            ) : (
              <p className="text-gray-500">No resume parsed yet.</p>
            )}
          </CardContent>
        </Card>

        {/* Save Button */}
        <Button
          onClick={async () => {
            if (!parsedData) return;
            try {
              const res = await fetch("http://127.0.0.1:8000/update/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ parsed: parsedData }),
              });
              const data = await res.json();
              if (data.pdf_url) {
                setPdfUrl(data.pdf_url + "?t=" + new Date().getTime());
              }
            } catch (err) {
              console.error("Update failed", err);
            }
          }}
        >
          💾 Save & Update Preview
        </Button>
      </div>

      {/* Right Side: PDF Preview */}
      <div className="w-1/3 border-l border-gray-300 flex flex-col p-4">
        <Card className="flex-grow bg-[#042F40]">
          <CardHeader>
            <CardTitle className="text-lg text-white">📑 Resume Preview</CardTitle>
          </CardHeader>
          <CardContent className="flex-grow ">
            {pdfUrl ? (
              <iframe src={pdfUrl} className="w-full h-[85vh] border rounded" title="Resume Preview" />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No preview available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default App;
