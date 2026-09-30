# [M] CVE-2016-9798

## Summary
Severity: Medium
Advisory: CVE-2016-9798
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-12-03
Source: https://osv.dev/vulnerability/CVE-2016-9798
Type: osv

## Details
In BlueZ 5.42, a use-after-free was identified in "conf_opt" function in "tools/parser/l2cap.c" source file. This issue can be triggered by processing a corrupted dump file and will result in hcidump crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00069.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00071.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00072.html
- http://www.securityfocus.com/bid/94652
- https://www.spinics.net/lists/linux-bluetooth/msg68892.html
