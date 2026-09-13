# [M] CVE-2025-61505

## Summary
Severity: Medium
Advisory: CVE-2025-61505
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/CVE-2025-61505
Type: osv

## Details
e107 CMS thru 2.3.3 are vulnerable to insecure deserialization in the `install.php` script. The script processes user-controlled input in the `previous_steps` POST parameter using `unserialize(base64_decode())` without validation, allowing attackers to craft malicious serialized data. This could lead to remote code execution, arbitrary file operations, or denial of service, depending on available PHP object gadgets in the codebase.

## References
- https://github.com/e107inc/e107/blob/master/install.php
- https://xancatos.org/cve202561505
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61505.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61505
