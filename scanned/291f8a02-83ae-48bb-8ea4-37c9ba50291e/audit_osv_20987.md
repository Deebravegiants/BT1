# [C] CVE-2021-39274

## Summary
Severity: Critical
Advisory: CVE-2021-39274
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-19
Source: https://osv.dev/vulnerability/CVE-2021-39274
Type: osv

## Details
In XeroSecurity Sn1per 9.0 (free version), insecure directory permissions (0777) are set during installation, allowing an unprivileged user to modify the main application and the application configuration file. This results in arbitrary code execution with root privileges.

## References
- https://github.com/1N3/Sn1per/releases
- https://github.com/1N3/Sn1per/issues/357
- https://github.com/nikip72/CVE-2021-39273-CVE-2021-39274
