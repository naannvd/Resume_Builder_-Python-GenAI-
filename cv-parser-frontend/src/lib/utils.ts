import { clsx , type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

// Combines conditional class names with Tailwind merging
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
