# [H] CVE-2019-7283

## Summary
Severity: High
Advisory: CVE-2019-7283
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2019-7283
Type: osv

## Details
An issue was discovered in rcp in NetKit through 0.17. For an rcp operation, the server chooses which files/directories are sent to the client. However, the rcp client only performs cursory validation of the object name returned. A malicious rsh server (or Man-in-The-Middle attacker) can overwrite arbitrary files in a directory on the rcp client machine. This is similar to CVE-2019-6111.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00016.html
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://bugs.debian.org/920486
