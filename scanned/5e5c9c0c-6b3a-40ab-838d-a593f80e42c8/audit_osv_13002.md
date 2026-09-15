# [M] CVE-2018-16845

## Summary
Severity: Medium
Advisory: CVE-2018-16845
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-16845
Type: osv

## Details
nginx before versions 1.15.6, 1.14.1 has a vulnerability in the ngx_http_mp4_module, which might allow an attacker to cause infinite loop in a worker process, cause a worker process crash, or might result in worker process memory disclosure by using a specially crafted mp4 file. The issue only affects nginx if it is built with the ngx_http_mp4_module (the module is not built by default) and the .mp4. directive is used in the configuration file. Further, the attack is only possible if an attacker is able to trigger processing of a specially crafted mp4 file with the ngx_http_mp4_module.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00035.html
- http://seclists.org/fulldisclosure/2021/Sep/36
- http://www.securityfocus.com/bid/105868
- http://www.securitytracker.com/id/1042039
- https://access.redhat.com/errata/RHSA-2018:3652
- https://access.redhat.com/errata/RHSA-2018:3653
- https://access.redhat.com/errata/RHSA-2018:3680
- https://access.redhat.com/errata/RHSA-2018:3681
- https://lists.debian.org/debian-lts-announce/2018/11/msg00010.html
- https://support.apple.com/kb/HT212818
- https://www.debian.org/security/2018/dsa-4335
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16845
- http://mailman.nginx.org/pipermail/nginx-announce/2018/000221.html
- https://usn.ubuntu.com/3812-1/
