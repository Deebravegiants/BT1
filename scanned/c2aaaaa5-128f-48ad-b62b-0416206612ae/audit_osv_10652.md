# [H] CVE-2017-17935

## Summary
Severity: High
Advisory: CVE-2017-17935
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17935
Type: osv

## Details
The File_read_line function in epan/wslua/wslua_file.c in Wireshark through 2.2.11 does not properly strip '\n' characters, which allows remote attackers to cause a denial of service (buffer underflow and application crash) via a crafted packet that triggers the attempted processing of an empty line.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=137ab7d5681486c6d6cc8faac4300b7cd4ec0cf1
- http://www.securityfocus.com/bid/102311
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14295
- https://code.wireshark.org/review/#/c/24997/
