# [M] CVE-2016-5355

## Summary
Severity: Medium
Advisory: CVE-2016-5355
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-5355
Type: osv

## Details
wiretap/toshiba.c in the Toshiba file parser in Wireshark 1.12.x before 1.12.12 and 2.x before 2.0.4 mishandles sscanf unsigned-integer processing, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91140
- http://www.debian.org/security/2016/dsa-3615
- https://www.wireshark.org/security/wnpa-sec-2016-34.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12394
- https://github.com/wireshark/wireshark/commit/3270dfac43da861c714df76513456b46765ff47f
- https://github.com/wireshark/wireshark/commit/5efb45231671baa2db2011d8f67f9d6e72bc455b
- http://www.openwall.com/lists/oss-security/2016/06/09/3
