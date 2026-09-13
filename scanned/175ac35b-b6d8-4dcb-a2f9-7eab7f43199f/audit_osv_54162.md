# [C] CVE-2023-40619

## Summary
Severity: Critical
Advisory: CVE-2023-40619
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/CVE-2023-40619
Type: osv

## Details
phpPgAdmin 7.14.4 and earlier is vulnerable to deserialization of untrusted data which may lead to remote code execution because user-controlled data is directly passed to the PHP 'unserialize()' function in multiple places. An example is the functionality to manage tables in 'tables.php' where the 'ma[]' POST parameter is deserialized.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00000.html
- https://github.com/dub-flow/vulnerability-research/tree/main/CVE-2023-40619
