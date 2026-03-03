<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => ['message' => 'Method not allowed. Use POST.']]);
    exit;
}

// Read Groq API key from Azure environment variable
$groqApiKey = getenv('GROQ_API_KEY');
if (!$groqApiKey) {
    http_response_code(500);
    echo json_encode(['error' => ['message' => 'GROQ_API_KEY not configured on server.']]);
    exit;
}

// Read request body
$input = json_decode(file_get_contents('php://input'), true);
if (!$input || !isset($input['messages']) || !is_array($input['messages'])) {
    http_response_code(400);
    echo json_encode(['error' => ['message' => 'Missing messages array in request body.']]);
    exit;
}

// Call Groq API
$payload = json_encode([
    'model' => 'llama-3.3-70b-versatile',
    'messages' => $input['messages'],
    'temperature' => 0.7,
    'max_tokens' => 512
]);

$ch = curl_init('https://api.groq.com/openai/v1/chat/completions');
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $payload,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'Authorization: Bearer ' . $groqApiKey
    ]
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

if ($curlError) {
    http_response_code(502);
    echo json_encode(['error' => ['message' => 'Failed to connect to Groq API: ' . $curlError]]);
    exit;
}

http_response_code($httpCode);
echo $response;
