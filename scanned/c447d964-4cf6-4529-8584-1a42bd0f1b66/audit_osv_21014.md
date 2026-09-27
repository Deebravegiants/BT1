# [H] CVE-2021-39500

## Summary
Severity: High
Advisory: CVE-2021-39500
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-39500
Type: osv

## Details
Eyoucms 1.5.4 is vulnerable to Directory Traversal. Due to a lack of input data sanitizaton in param tpldir, filename, type, nid an attacker can inject "../" to escape and write file to writeable directories.

## References
- https://github.com/KietNA-HPT/CVE
- https://github.com/eyoucms/eyoucms/releases/tag/v1.5.4
