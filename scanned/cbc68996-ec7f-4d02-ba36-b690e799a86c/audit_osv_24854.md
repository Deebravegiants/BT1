# [H] CVE-2023-27706

## Summary
Severity: High
Advisory: CVE-2023-27706
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-06-09
Source: https://osv.dev/vulnerability/CVE-2023-27706
Type: osv

## Details
Bitwarden Windows desktop application versions prior to v2023.4.0 store biometric keys in Windows Credential Manager, accessible to other local unprivileged processes.

## References
- https://github.com/bitwarden/clients/blob/8b5a223ad4ca0f89b6c9bcdbddef464d1755d2c0/apps/desktop/desktop_native/src/biometric/windows.rs#L19
- https://github.com/bitwarden/clients/blob/8b5a223ad4ca0f89b6c9bcdbddef464d1755d2c0/apps/desktop/desktop_native/src/password/windows.rs#L16
- https://hackerone.com/reports/1874155
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27706.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27706
- https://github.com/bitwarden/clients
