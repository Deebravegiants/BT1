# [C] CVE-2016-8704

## Summary
Severity: Critical
Advisory: CVE-2016-8704
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-8704
Type: osv

## Details
An integer overflow in the process_bin_append_prepend function in Memcached, which is responsible for processing multiple commands of Memcached binary protocol, can be abused to cause heap overflow and lead to remote code execution.

## References
- http://www.securityfocus.com/bid/94083
- http://www.securitytracker.com/id/1037333
- http://rhn.redhat.com/errata/RHSA-2016-2819.html
- http://rhn.redhat.com/errata/RHSA-2016-2820.html
- http://www.debian.org/security/2016/dsa-3704
- https://access.redhat.com/errata/RHSA-2017:0059
- https://security.gentoo.org/glsa/201701-12
- http://www.talosintelligence.com/reports/TALOS-2016-0219/
