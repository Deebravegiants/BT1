# [H] CVE-2012-6698

## Summary
Severity: High
Advisory: CVE-2012-6698
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-11
Source: https://osv.dev/vulnerability/CVE-2012-6698
Type: osv

## Details
The decode_search function in dhcp.c in dhcpcd 3.x allows remote DHCP servers to cause a denial of service (out-of-bounds write) via a crafted response.

## References
- http://www.debian.org/security/2016/dsa-3534
- http://www.openwall.com/lists/oss-security/2015/12/02/1
- http://www.openwall.com/lists/oss-security/2015/12/03/1
- https://bugs.launchpad.net/ubuntu/+source/dhcpcd/+bug/1517226
- https://launchpadlibrarian.net/228152582/dhcp.c.patch
