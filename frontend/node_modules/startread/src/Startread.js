// Importing necessary CSS files for styling
import './css/startread_styles.css';
import './css/AnnotationLayer.css';
import './css/TextLayer.css';

// Importing React and necessary hooks
import React, { useState } from 'react';

// Importing components from react-pdf library
import { Document, Page, pdfjs } from "react-pdf";

// Setting the worker source for pdfjs
pdfjs.GlobalWorkerOptions.workerSrc = `${process.env.PUBLIC_URL}/pdf.worker.min.mjs`;

// Main component that renders the Startread component
export default function Startread() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileName, setFileName] = useState('Sample book name goes here');
    const [isFileUploaded, setIsFileUploaded] = useState(false);

    const handleFileUpload = async (file) => {
        if (file && file.type === 'application/pdf') {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('http://localhost:5000/api/upload-pdf', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    setSelectedFile(file);
                    setFileName(file.name);
                    setIsFileUploaded(true);
                } else {
                    alert('Error uploading file');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error uploading file');
            }
        } else {
            alert('Please select a PDF file');
        }
    };

    return (
        <div className="container">
            <MainContainer 
                selectedFile={selectedFile}
                fileName={fileName}
                onFileUpload={handleFileUpload}
                isFileUploaded={isFileUploaded}
            />
        </div>
    );
}

// MainContainer component that contains the main functionality
function MainContainer({ selectedFile, fileName, onFileUpload, isFileUploaded }) {
    const pageNum = 1;
    const [time, setTime] = useState(10);
    const [isDragging, setIsDragging] = useState(false);

    const calculateTimeFromPosition = (event, container) => {
        const rect = container.getBoundingClientRect();
        const offsetX = event.clientX - rect.left;
        const width = rect.width;
        return Math.min(120, Math.max(5, Math.round((offsetX / width) * 120)));
    };

    const handleClick = (event) => {
        const progressContainer = event.currentTarget;
        const newTime = calculateTimeFromPosition(event, progressContainer);
        setTime(newTime);
    };

    const handleMouseDown = () => {
        setIsDragging(true);
    };

    const handleMouseMove = (event) => {
        if (isDragging) {
            const progressContainer = event.currentTarget;
            const newTime = calculateTimeFromPosition(event, progressContainer);
            setTime(newTime);
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    const handleSelectDifferentBook = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/pdf';
        input.onchange = (e) => {
            const file = e.target.files[0];
            onFileUpload(file);
        };
        input.click();
    };

    const handleStartReading = () => {
        if (selectedFile) {
            const redirectUrl = new URL('http://localhost:3003/');
            redirectUrl.searchParams.append('readingTime', time);
            redirectUrl.searchParams.append('pdfFile', selectedFile.name);
            
            window.location.href = redirectUrl.toString();
        } else {
            alert('Please select a PDF file first');
        }
    };

    return (
        <div>
            <div className="new-reading">
                <div className="left-side">
                    <h4>Book selected</h4>
                    <div className="pdf-thumbnail-holder">
                        <Document
                            file={selectedFile || `${process.env.PUBLIC_URL}/imgtemp/example.pdf`}
                            onLoadError={(error) => console.log("Error loading PDF:", error)}
                            onSourceError={(error) => console.log("Error with PDF source:", error)}
                        >
                            <Page pageNumber={1} width={220} />
                        </Document>
                    </div>
                    <p>{fileName}</p>
                    <p id="pageNumber">Page {pageNum}</p>
                    <button className="home-btn" onClick={handleSelectDifferentBook}>
                        Select different book
                    </button>
                </div>
                <div className="right-side">
                    <h4>Set reading length</h4>
                    <div className="timer-container">
                        <div className="timer-timeDisplay">
                            <p><span>{time}</span> min</p>
                        </div>
                        <div
                            className="timer-progressContainer"
                            onClick={handleClick}
                            onMouseDown={handleMouseDown}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                            onMouseLeave={handleMouseUp}
                        >
                            <div
                                className="timer-progressBar"
                                style={{ width: `${(time / 120) * 100}%` }}
                            />
                        </div>
                    </div>
                    <button className="home-btn" onClick={handleStartReading}>
                        Start reading
                    </button>
                </div>
            </div>
        </div>
    );
}
