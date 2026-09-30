# [C] emlog Arbitrary File Upload Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-22799
Aliases: GHSA-p837-mrw9-5x5j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22799
Type: osv

## Details
Emlog is an open source website building system. emlog v2.6.1 and earlier exposes a REST API endpoint (/index.php?rest-api=upload) for media file uploads. The endpoint fails to implement proper validation of file types, extensions, and content, allowing authenticated attackers (with a valid API key or admin session cookie) to upload arbitrary files (including malicious PHP scripts) to the server. An attacker can obtain the API key either by gaining administrator access to enable the REST API setting, or via information disclosure vulnerabilities in the application. Once uploaded, the malicious PHP file can be executed to gain remote code execution (RCE) on the target server, leading to full server compromise.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22799.json
- https://github.com/emlog/emlog/security/advisories/GHSA-p837-mrw9-5x5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22799
- https://github.com/emlog/emlog/commit/429b02fda842254b9b9b39303e9161999c180560
