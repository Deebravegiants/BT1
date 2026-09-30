# [H] CVE-2016-7098

## Summary
Severity: High
Advisory: CVE-2016-7098
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-7098
Type: osv

## Details
Race condition in wget 1.17 and earlier, when used in recursive or mirroring mode to download a single file, might allow remote servers to bypass intended access list restrictions by keeping an HTTP connection open.

## References
- http://www.securityfocus.com/bid/93157
- https://lists.debian.org/debian-lts-announce/2020/01/msg00031.html
- https://www.exploit-db.com/exploits/40824/
- http://lists.opensuse.org/opensuse-updates/2017-01/msg00007.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00044.html
- http://www.openwall.com/lists/oss-security/2016/08/27/2
- http://lists.gnu.org/archive/html/bug-wget/2016-08/msg00134.html
- http://lists.gnu.org/archive/html/bug-wget/2016-08/msg00083.html
