# [M] CVE-2025-59028

## Summary
Severity: Medium
Advisory: CVE-2025-59028
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2025-59028
Type: osv

## Details
When sending invalid base64 SASL data, login process is disconnected from the auth server, causing all active authentication sessions to fail. Invalid BASE64 data can be used to DoS a vulnerable server to break concurrent logins. Install fixed version or disable concurrency in login processes (heavy perfomance penalty on large deployments). No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59028.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-59028
