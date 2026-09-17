# [H] CVE-2018-10058

## Summary
Severity: High
Advisory: CVE-2018-10058
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2018-10058
Type: osv

## Details
The remote management interface of cgminer 4.10.0 and bfgminer 5.5.0 allows an authenticated remote attacker to execute arbitrary code due to a stack-based buffer overflow in the addpool, failover-only, poolquota, and save command handlers.

## References
- http://www.openwall.com/lists/oss-security/2018/06/03/1
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2018-10058
