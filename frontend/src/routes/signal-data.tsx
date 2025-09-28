import React, {useState} from 'react';
import {createFileRoute} from '@tanstack/react-router';
import axios from 'axios';
import {
  Box,
  Container,
  Input as ChakraInput,
  Table,
  Text
} from '@chakra-ui/react';
import {Button} from "../components/ui/button";
import {useMutation, useQuery} from '@tanstack/react-query';

// Define the route for this component
export const Route = createFileRoute("/signal-data")({
  component: SignalData,
});

interface UploadedFile {
  id: string;
  filename: string;
  upload_timestamp: string;
  status: string;
  file_type: string;
}

function SignalData() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileDetails, setFileDetails] = useState<UploadedFile | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadStatus, setUploadStatus] = useState<string>('');

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // --- useQuery for uploaded files ---
  const {
    data: uploadedFiles = [],
    isLoading,
    error: fetchError,
    refetch: refetchUploadedFiles,
  } = useQuery({
    queryKey: ['uploadedFiles'],
    queryFn: async () => {
      const response = await axios.get<UploadedFile[]>(`${API_BASE_URL}/api/v1/uploaded-files`);
      return response.data;
    },
  });

  const fetchFileDetails = async (fileId: string) => {
    try {
      const response = await axios.get<UploadedFile>(`${API_BASE_URL}/api/v1/uploaded-files/${fileId}`);
      setFileDetails(response.data);
      setShowModal(true);
    } catch (err: any) {
      setLocalError('Failed to fetch file details.');
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setUploadStatus('');
      setLocalError(null);
    } else {
      setSelectedFile(null);
    }
  };

  const handleShowDetails = (fileId: string) => {
    void fetchFileDetails(fileId);
  };

  // --- useMutation for upload ---
  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      setUploadProgress(0);
      setUploadStatus('Uploading...');
      setLocalError(null);
      const formData = new FormData();
      formData.append('file', file);
      const response = await axios.post<UploadedFile>(
        `${API_BASE_URL}/api/v1/upload-signal-data`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
            }
          },
        }
      );
      return response.data;
    },
    onSuccess: (data) => {
      setUploadStatus(`Upload successful! File ID: ${data.id}, Status: ${data.status}`);
      setSelectedFile(null);
      setUploadProgress(0);
      refetchUploadedFiles();
    },
    onError: (err: any) => {
      setUploadProgress(0);
      setLocalError(`Upload failed: ${err.response?.data?.detail || err.message || 'Unknown error'}`);
    },
    onSettled: () => {
      setUploadProgress(0);
    },
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }
    uploadMutation.mutate(selectedFile);
  };

  return (
    <Container maxW="container.xl" py={8}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
        <Text fontSize="3xl" fontWeight="bold">
          Signal Data Management
        </Text>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="md">
          <Text fontSize="xl" mb={4}>
            Upload New Signal File
          </Text>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <ChakraInput
              type="file"
              onChange={handleFileChange}
              p={1}
              border="none"
              _focus={{ boxShadow: 'none' }}
            />
            <Button onClick={handleUpload} loading={uploadMutation.isLoading} disabled={!selectedFile} colorScheme="teal">
              Upload File
            </Button>
            <Button onClick={() => refetchUploadedFiles()} disabled={uploadMutation.isLoading} colorScheme="gray" variant="outline">
              Refresh List
            </Button>
          </div>
          {uploadProgress > 0 && uploadProgress < 100 && (
            <Box mt={2} w="100%">
              <Text fontSize="sm">Uploading: {uploadProgress}%</Text>
            </Box>
          )}
          {uploadStatus && <Text mt={2} color="green.500">{uploadStatus}</Text>}
          {(localError || uploadMutation.error || fetchError) && (
            <div style={{ background: '#FED7D7', color: '#C53030', padding: 8, borderRadius: 4, marginTop: 16 }}>
              {localError || (uploadMutation.error as any)?.message || (fetchError as any)?.message}
            </div>
          )}
        </Box>
        <Box p={5} shadow="md" borderWidth="1px" borderRadius="md">
          <Text fontSize="xl" mb={4}>
            Uploaded Files
          </Text>
          {isLoading ? (
            <div style={{ padding: 16, textAlign: 'center' }}>Loading...</div>
          ) : uploadedFiles.length === 0 ? (
            <Text>No files uploaded yet.</Text>
          ) : (
            <Table.Root size={{ base: "sm", md: "md" }}>
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeader w="sm">Filename</Table.ColumnHeader>
                  <Table.ColumnHeader w="sm">Upload Time</Table.ColumnHeader>
                  <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
                  <Table.ColumnHeader w="sm">File Type</Table.ColumnHeader>
                  <Table.ColumnHeader w="sm">ID</Table.ColumnHeader>
                  <Table.ColumnHeader w="sm">Details</Table.ColumnHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {uploadedFiles.map((file) => (
                  <Table.Row key={file.id}>
                    <Table.Cell truncate maxW="sm">{file.filename}</Table.Cell>
                    <Table.Cell truncate maxW="sm">{new Date(file.upload_timestamp).toLocaleString()}</Table.Cell>
                    <Table.Cell truncate maxW="sm">{file.status}</Table.Cell>
                    <Table.Cell truncate maxW="sm">{file.file_type}</Table.Cell>
                    <Table.Cell truncate maxW="sm">{file.id}</Table.Cell>
                    <Table.Cell>
                      <Button size="sm" onClick={() => handleShowDetails(file.id)}>
                        View
                      </Button>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          )}
        </Box>
        {showModal && fileDetails && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              width: '100vw',
              height: '100vh',
              background: 'rgba(0,0,0,0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
            onClick={() => setShowModal(false)}
          >
            <div
              style={{ background: '#fff', padding: 32, borderRadius: 8, minWidth: 320 }}
              onClick={e => e.stopPropagation()}
            >
              <h2 style={{ fontSize: 20, marginBottom: 16 }}>File Details</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <span><b>Filename:</b> {fileDetails.filename}</span>
                <span><b>Status:</b> {fileDetails.status}</span>
                <span><b>File Type:</b> {fileDetails.file_type}</span>
                <span><b>Upload Time:</b> {new Date(fileDetails.upload_timestamp).toLocaleString()}</span>
                <span><b>ID:</b> {fileDetails.id}</span>
              </div>
              <Button style={{ marginTop: 24 }} onClick={() => setShowModal(false)}>
                Close
              </Button>
            </div>
          </div>
        )}
      </div>
    </Container>
  );
}

export default SignalData;
