# [M] CVE-2025-57055

## Summary
Severity: Medium
Advisory: CVE-2025-57055
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-57055
Type: osv

## Details
WonderCMS 3.5.0 is vulnerable to Server-Side Request Forgery (SSRF) in the custom module installation functionality. An authenticated administrator can supply a malicious URL via the pluginThemeUrl POST parameter. The server fetches the provided URL using curl_exec() without sufficient validation, allowing the attacker to force internal or external HTTP requests.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57055.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57055
- https://github.com/thawphone/CVE-2025-57055
