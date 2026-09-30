# [C] CVE-2020-13452

## Summary
Severity: Critical
Advisory: CVE-2020-13452
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-13452
Type: osv

## Details
In Gotenberg through 6.2.1, insecure permissions for tini (writable by user gotenberg) potentially allow an attacker to overwrite the file, which can lead to denial of service or code execution.

## References
- http://packetstormsecurity.com/files/160744/Gotenberg-6.2.0-Traversal-Code-Execution-Insecure-Permissions.html
- https://github.com/thecodingmachine/gotenberg/issues/199
