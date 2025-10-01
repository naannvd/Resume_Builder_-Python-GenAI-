export interface ResumeData {
  full_name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  education?: string[];
  projects?: string[];
  experience?: string[];
  skills?: string[];
  certifications?: string[];
  languages?: string[];
  [key: string]: unknown; // fallback for unexpected fields
}
