# [M] Insertion of Sensitive Information into Log in codeigniter4/shield

## Summary
Severity: Medium
Advisory: CVE-2023-48708
Aliases: GHSA-j72f-h752-mx4w
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-11-24
Source: https://osv.dev/vulnerability/CVE-2023-48708
Type: osv

## Details
CodeIgniter Shield is an authentication and authorization provider for CodeIgniter 4. In affected versions successful login attempts are recorded with the raw tokens stored in the log table. If a malicious person somehow views the data in the log table they can obtain a raw token which can then be used to send a request with that user's authority. This issue has been addressed in version 1.0.0-beta.8. Users are advised to upgrade. Users unable to upgrade should disable logging for successful login attempts by the configuration files.

## References
- https://codeigniter4.github.io/shield/getting_started/authenticators/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48708.json
- https://github.com/codeigniter4/shield/security/advisories/GHSA-j72f-h752-mx4w
- https://nvd.nist.gov/vuln/detail/CVE-2023-48708
- https://github.com/codeigniter4/shield/commit/7e84c3fb3411294f70890819bfe51781bb9dc8e4
