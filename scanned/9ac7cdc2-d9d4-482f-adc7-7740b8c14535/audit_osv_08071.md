# [H] CVE-2016-10189

## Summary
Severity: High
Advisory: CVE-2016-10189
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2016-10189
Type: osv

## Details
BitlBee before 3.5 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) and possibly execute arbitrary code via a file transfer request for a contact that is not in the contact list.

## References
- http://www.securityfocus.com/bid/95931
- http://www.debian.org/security/2017/dsa-3853
- http://www.openwall.com/lists/oss-security/2017/01/30/4
- http://www.openwall.com/lists/oss-security/2017/01/31/11
- https://bugs.bitlbee.org/ticket/1282
- https://github.com/bitlbee/bitlbee/commit/701ab8129ba9ea64f569daedca9a8603abad740f
