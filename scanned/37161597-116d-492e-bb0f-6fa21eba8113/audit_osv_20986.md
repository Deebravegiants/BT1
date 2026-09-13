# [H] CVE-2021-39273

## Summary
Severity: High
Advisory: CVE-2021-39273
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-19
Source: https://osv.dev/vulnerability/CVE-2021-39273
Type: osv

## Details
In XeroSecurity Sn1per 9.0 (free version), insecure permissions (0777) are set upon application execution, allowing an unprivileged user to modify the application, modules, and configuration files. This leads to arbitrary code execution with root privileges.

## References
- https://github.com/1N3/Sn1per/releases
- https://github.com/1N3/Sn1per/issues/358
- https://github.com/nikip72/CVE-2021-39273-CVE-2021-39274
