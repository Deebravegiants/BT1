# [M] CVE-2022-0530

## Summary
Severity: Medium
Advisory: CVE-2022-0530
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-09
Source: https://osv.dev/vulnerability/CVE-2022-0530
Type: osv

## Details
A flaw was found in Unzip. The vulnerability occurs during the conversion of a wide string to a local string that leads to a heap of out-of-bound write. This flaw allows an attacker to input a specially crafted zip file, leading to a crash or code execution.

## References
- https://support.apple.com/kb/HT213257
- http://seclists.org/fulldisclosure/2022/May/33
- https://support.apple.com/kb/HT213255
- https://www.debian.org/security/2022/dsa-5202
- http://seclists.org/fulldisclosure/2022/May/35
- http://seclists.org/fulldisclosure/2022/May/38
- https://lists.debian.org/debian-lts-announce/2022/09/msg00028.html
- https://security.gentoo.org/glsa/202310-17
- https://support.apple.com/kb/HT213256
- https://bugzilla.redhat.com/show_bug.cgi?id=2051395
- https://github.com/ByteHackr/unzip_poc
