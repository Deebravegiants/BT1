# [H] CVE-2018-16843

## Summary
Severity: High
Advisory: CVE-2018-16843
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-16843
Type: osv

## Details
nginx before versions 1.15.6 and 1.14.1 has a vulnerability in the implementation of HTTP/2 that can allow for excessive memory consumption. This issue affects nginx compiled with the ngx_http_v2_module (not compiled by default) if the 'http2' option of the 'listen' directive is used in a configuration file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00035.html
- http://mailman.nginx.org/pipermail/nginx-announce/2018/000220.html
- http://seclists.org/fulldisclosure/2021/Sep/36
- http://www.securityfocus.com/bid/105868
- http://www.securitytracker.com/id/1042038
- https://access.redhat.com/errata/RHSA-2018:3653
- https://access.redhat.com/errata/RHSA-2018:3680
- https://access.redhat.com/errata/RHSA-2018:3681
- https://support.apple.com/kb/HT212818
- https://usn.ubuntu.com/3812-1/
- https://www.debian.org/security/2018/dsa-4335
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16843
