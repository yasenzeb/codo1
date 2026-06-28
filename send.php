<?php
// ===== Telegram bot config =====
// Replace with your real values
$BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE";
$CHAT_ID   = "PUT_YOUR_CHAT_ID_HERE";

// CORS (allow form to call from any origin; tighten in production)
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=utf-8");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["ok" => false, "error" => "Method not allowed"]);
    exit;
}

// Read JSON body
$raw = file_get_contents("php://input");
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(["ok" => false, "error" => "Invalid JSON"]);
    exit;
}

// Build a readable message
function esc($s){ return htmlspecialchars((string)$s, ENT_QUOTES, "UTF-8"); }

$lang     = $data["lang"] ?? "en";
$business = $data["business"] ?? "-";
$answers  = $data["answers"] ?? [];
$ip       = $_SERVER["REMOTE_ADDR"] ?? "-";
$ua       = $_SERVER["HTTP_USER_AGENT"] ?? "-";
$time     = date("Y-m-d H:i:s");

$lines = [];
$lines[] = "<b>📊 New Business Analysis</b>";
$lines[] = "🕒 " . esc($time);
$lines[] = "🌐 Lang: " . esc($lang);
$lines[] = "🏷 Business: <b>" . esc($business) . "</b>";
$lines[] = "";
$lines[] = "<b>Answers:</b>";
foreach ($answers as $a) {
    $q = esc($a["question"] ?? "");
    $v = $a["answer"] ?? "";
    if (is_array($v)) $v = implode(", ", $v);
    $lines[] = "• <b>" . $q . ":</b> " . esc($v);
}
$lines[] = "";
$lines[] = "🧭 IP: " . esc($ip);
$lines[] = "🖥 UA: " . esc(substr($ua, 0, 200));

$text = implode("\n", $lines);

// Send to Telegram
$url = "https://api.telegram.org/bot{$BOT_TOKEN}/sendMessage";
$payload = http_build_query([
    "chat_id"    => $CHAT_ID,
    "text"       => $text,
    "parse_mode" => "HTML",
    "disable_web_page_preview" => true,
]);

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $payload,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT        => 15,
]);
$resp = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$err  = curl_error($ch);
curl_close($ch);

if ($resp === false || $code >= 400) {
    http_response_code(502);
    echo json_encode(["ok" => false, "error" => "Telegram failed", "details" => $err ?: $resp]);
    exit;
}

echo json_encode(["ok" => true]);