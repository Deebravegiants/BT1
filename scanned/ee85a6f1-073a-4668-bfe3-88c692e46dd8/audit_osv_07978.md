# [M] CVE-2016-0747

## Summary
Severity: Medium
Advisory: CVE-2016-0747
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2016-02-15
Source: https://osv.dev/vulnerability/CVE-2016-0747
Type: osv

## Details
The resolver in nginx before 1.8.1 and 1.9.x before 1.9.10 does not properly limit CNAME resolution, which allows remote attackers to cause a denial of service (worker process resource consumption) via vectors related to arbitrary name resolution.

## References
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00042.html
- http://mailman.nginx.org/pipermail/nginx/2016-January/049700.html
- http://seclists.org/fulldisclosure/2021/Sep/36
- http://www.debian.org/security/2016/dsa-3473
- http://www.securitytracker.com/id/1034869
- http://www.ubuntu.com/usn/USN-2892-1
- https://access.redhat.com/errata/RHSA-2016:1425
- https://bto.bluecoat.com/security-advisory/sa115
- https://security.gentoo.org/glsa/201606-06
- https://support.apple.com/kb/HT212818
- https://bugzilla.redhat.com/show_bug.cgi?id=1302589
