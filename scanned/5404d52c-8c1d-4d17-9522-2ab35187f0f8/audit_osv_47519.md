# [M] CVE-2016-7498

## Summary
Severity: Medium
Advisory: CVE-2016-7498
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/CVE-2016-7498
Type: osv

## Details
OpenStack Compute (nova) 13.0.0 does not properly delete instances from compute nodes, which allows remote authenticated users to cause a denial of service (disk consumption) by deleting instances while in the resize state.  NOTE: this vulnerability exists because of a CVE-2015-3280 regression.

## References
- http://www.openwall.com/lists/oss-security/2016/09/21/8
- http://www.openwall.com/lists/oss-security/2016/09/23/1
- http://www.securityfocus.com/bid/93068
- https://security.openstack.org/ossa/OSSA-2016-011.html
