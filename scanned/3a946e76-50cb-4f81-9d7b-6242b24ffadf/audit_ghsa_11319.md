# [H] Salvo Affected by Denial of Service via Unbounded Memory Allocation in Form Data Parsing

## Summary
Severity: High
Advisory: GHSA-pp9r-xg4c-8j4x
CVE: CVE-2026-33241
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-pp9r-xg4c-8j4x
Type: github-advisory

## Affected
- crates.io: `salvo` — affected >=0 <0.89.3

## Details
## Summary
Salvo's form data parsing implementations (`form_data()` method and `Extractible` macro) do not enforce payload size limits before reading request bodies into memory. This allows attackers to cause Out-of-Memory (OOM) conditions by sending extremely large payloads, leading to service crashes and denial of service.

## Details
### Vulnerability Description
Three attack vectors exist in Salvo's form handling:

1. **URL-encoded form data** (`application/x-www-form-urlencoded`)
   - `Request::form_data()` calls `BodyExt::collect(body)` which reads the entire body into memory without size checking
   - Affects handlers using `req.form_data().await` directly

2. **Multipart form data** (`multipart/form-data`)
   - Similar unbounded memory allocation during parsing
   - Affects handlers processing multipart uploads

3. **Extractible macro**
   - `#[derive(Extractible)]` with `#[salvo(extract(default_source(from = "body")))]` internally calls `form_data()`
   - Vulnerabilities propagate to all extractors using body sources

### Root Cause
The `FormData::read()` implementation prioritizes convenience over safety by reading entire request bodies before validation. Even when `Request::payload_with_max_size()` is available, it's not automatically applied in the form parsing path.

### PoC
1. run `Extract data from request` example in readme.md in docker file with limited memory say 100mb.
2. Send `application/x-www-form-urlencoded` OR `multipart/form-data` payload to the endpoint.
3. The server process OOM-crashes, instead of returning 413 error.


## Impact
### Immediate Effects
- **Service Unavailability**: Servers crash under memory pressure
- **Resource Exhaustion**: Single request can consume all available memory
- **Cascading Failures**: In containerized environments, OOM can affect other services

### Attack Characteristics
- **Low Cost**: Attacker needs minimal bandwidth (header only, body can be streamed)
- **No Authentication**: Exploitable on public endpoints
- **Difficult to Rate-Limit**: Traditional rate limiting may not prevent single large request
- **Amplification**: Small network cost → large memory consumption

### Real-World Scenarios
1. Public API endpoints accepting form data
2. User registration/profile update handlers
3. File upload endpoints using multipart forms
4. Any endpoint using `#[derive(Extractible)]` with body sources

## Suggestion: Make Multipart File Upload Handling Explicit Opt-In

### Problem Statement

Currently, Salvo's multipart form data parsing automatically handles file uploads without explicit developer intent. This creates several security and usability concerns:

1. **Unintended File Storage**: Developers may unknowingly accept file uploads when they only intended to handle text fields
2. **Disk Space Exhaustion**: Automatic file buffering to disk can fill storage without proper limits
3. **Resource Cleanup**: Temporary files may not be properly cleaned up if handlers don't expect them
4. **Attack Surface**: Endpoints inadvertently become file upload targets

## References
- https://github.com/salvo-rs/salvo/security/advisories/GHSA-pp9r-xg4c-8j4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33241
- https://github.com/salvo-rs/salvo
- https://github.com/salvo-rs/salvo/releases/tag/v0.89.3
