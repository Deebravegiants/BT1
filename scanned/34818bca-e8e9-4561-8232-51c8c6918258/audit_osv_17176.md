# [C] CVE-2020-13450

## Summary
Severity: Critical
Advisory: CVE-2020-13450
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2020-13450
Type: osv

## Details
A directory traversal vulnerability in file upload function of Gotenberg through 6.2.1 allows an attacker to upload and overwrite any writable files outside the intended folder. This can lead to DoS, a change to program behavior, or code execution.

## References
- https://github.com/thecodingmachine/gotenberg/issues/199
- http://packetstormsecurity.com/files/160744/Gotenberg-6.2.0-Traversal-Code-Execution-Insecure-Permissions.html
