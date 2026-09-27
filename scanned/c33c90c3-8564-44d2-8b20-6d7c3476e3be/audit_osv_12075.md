# [M] CVE-2018-10057

## Summary
Severity: Medium
Advisory: CVE-2018-10057
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-10057
Type: osv

## Details
The remote management interface of cgminer 4.10.0 and bfgminer 5.5.0 allows an authenticated remote attacker to write the miner configuration file to arbitrary locations on the server due to missing basedir restrictions (absolute directory traversal).

## References
- http://www.openwall.com/lists/oss-security/2018/06/03/1
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2018-10057
