# [C] h2oGPT 0.2.1 Path Traversal via OpenAI-compatible Files API

## Summary
Severity: Critical
Advisory: CVE-2026-65700
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65700
Type: osv

## Details
h2oGPT through 0.2.1 contains a path traversal vulnerability in the OpenAI-compatible files API that allows unauthenticated remote attackers to read, write, and delete arbitrary files accessible to the server process by supplying traversal sequences in the bearer token. The get_user_dir function in openai_server/backend_utils.py uses the bearer token string unsanitized as a path component via os.path.join, and because the default API key is EMPTY authentication is bypassed, enabling attackers to traverse outside the intended user directory through the file content, delete, and upload endpoints to achieve remote code execution by writing to startup hooks or application-loaded files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65700.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65700
- https://www.vulncheck.com/advisories/h2ogpt-path-traversal-via-openai-compatible-files-api
- https://github.com/h2oai/h2ogpt
- https://github.com/geo-chen/oss/blob/main/h2ogpt.md
