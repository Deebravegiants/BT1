# [C] CVE-2016-0746

## Summary
Severity: Critical
Advisory: CVE-2016-0746
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-15
Source: https://osv.dev/vulnerability/CVE-2016-0746
Type: osv

## Details
Use-after-free vulnerability in the resolver in nginx 0.6.18 through 1.8.0 and 1.9.x before 1.9.10 allows remote attackers to cause a denial of service (worker process crash) or possibly have unspecified other impact via a crafted DNS response related to CNAME response processing.

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
- https://bugzilla.redhat.com/show_bug.cgi?id=1302588
