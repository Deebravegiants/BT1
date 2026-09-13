# [C] CVE-2018-1000550

## Summary
Severity: Critical
Advisory: CVE-2018-1000550
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000550
Type: osv

## Details
The Sympa Community Sympa version prior to version 6.2.32 contains a Directory Traversal vulnerability in wwsympa.fcgi template editing function that can result in Possibility to create or modify files on the server filesystem. This attack appear to be exploitable via HTTP GET/POST request. This vulnerability appears to have been fixed in 6.2.32.

## References
- https://usn.ubuntu.com/4442-1/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00033.html
- https://www.debian.org/security/2018/dsa-4285
- https://sympa-community.github.io/security/2018-001.html
