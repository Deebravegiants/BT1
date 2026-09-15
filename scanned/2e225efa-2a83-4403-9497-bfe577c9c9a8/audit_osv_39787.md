# [M] CVE-2026-47356

## Summary
Severity: Medium
Advisory: CVE-2026-47356
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-47356
Type: osv

## Details
Terrascan v1.18.3 and prior are vulnerable to Server-Side Request Forgery (SSRF) via the webhook_url parameter in the file scan endpoint (POST /v1/{iac}/{iacVersion}/{cloud}/local/file/scan) when running in server mode. An unauthenticated remote attacker can supply an arbitrary URL as the webhook_url multipart form parameter. After scanning the uploaded file, Terrascan sends an HTTP POST request to the attacker-controlled URL containing the full scan results as a JSON body, with the attacker-supplied webhook_token forwarded as a Bearer token in the Authorization header. The retryable HTTP client retries up to 10 times on failure. This affects deployments running terrascan in server mode (terrascan server), which binds to 0.0.0.0 with no authentication. Note: Terrascan was archived in August 2023 and no patch will be released.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47356.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-47356
- https://github.com/tenable/terrascan
