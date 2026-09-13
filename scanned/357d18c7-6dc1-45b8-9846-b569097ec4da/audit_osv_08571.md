# [H] CVE-2016-4450

## Summary
Severity: High
Advisory: CVE-2016-4450
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2016-4450
Type: osv

## Details
os/unix/ngx_files.c in nginx before 1.10.1 and 1.11.x before 1.11.1 allows remote attackers to cause a denial of service (NULL pointer dereference and worker process crash) via a crafted request, involving writing a client request body to a temporary file.

## References
- http://mailman.nginx.org/pipermail/nginx-announce/2016/000179.html
- http://www.debian.org/security/2016/dsa-3592
- http://www.securityfocus.com/bid/90967
- http://www.securitytracker.com/id/1036019
- http://www.ubuntu.com/usn/USN-2991-1
- https://access.redhat.com/errata/RHSA-2016:1425
- https://security.gentoo.org/glsa/201606-06
