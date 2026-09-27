# [C] CVE-2017-5668

## Summary
Severity: Critical
Advisory: CVE-2017-5668
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-14
Source: https://osv.dev/vulnerability/CVE-2017-5668
Type: osv

## Details
bitlbee-libpurple before 3.5.1 allows remote attackers to cause a denial of service (NULL pointer dereference and crash) and possibly execute arbitrary code via a file transfer request for a contact that is not in the contact list.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-10189.

## References
- http://www.securityfocus.com/bid/95932
- http://www.openwall.com/lists/oss-security/2017/01/30/4
- http://www.openwall.com/lists/oss-security/2017/01/31/11
- https://bugs.bitlbee.org/ticket/1282
- https://github.com/bitlbee/bitlbee/commit/30d598ce7cd3f136ee9d7097f39fa9818a272441
