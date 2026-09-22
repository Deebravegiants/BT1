# [H] Open WebUI allows Remote Code Execution via Arbitrary File Upload to /audio/api/v1/transcriptions

## Summary
Severity: High
Advisory: GHSA-ff5c-56m7-vc75
CVE: CVE-2024-8060
CWE: CWE-22, CWE-434
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-ff5c-56m7-vc75
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.5.17

## Details
OpenWebUI version 0.3.0 contains a vulnerability in the audio API endpoint `/audio/api/v1/transcriptions` that allows for arbitrary file upload. The application performs insufficient validation on the `file.content_type` and allows user-controlled filenames, leading to a path traversal vulnerability. This can be exploited by an authenticated user to overwrite critical files within the Docker container, potentially leading to remote code execution as the root user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8060
- https://github.com/open-webui/open-webui/commit/613a087387c094e71ee91d29c015195ef401e160
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/a3b1a4b7-c723-496d-842c-844cc0988fe9
