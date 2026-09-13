# [H] CVE-2020-15778

## Summary
Severity: High
Advisory: CVE-2020-15778
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-24
Source: https://osv.dev/vulnerability/CVE-2020-15778
Type: osv

## Details
scp in OpenSSH through 8.3p1 allows command injection in the scp.c toremote function, as demonstrated by backtick characters in the destination argument. NOTE: the vendor reportedly has stated that they intentionally omit validation of "anomalous argument transfers" because that could "stand a great chance of breaking existing workflows."

## References
- https://access.redhat.com/errata/RHSA-2024:3166
- https://news.ycombinator.com/item?id=25005567
- https://security.gentoo.org/glsa/202212-06
- https://security.netapp.com/advisory/ntap-20200731-0007/
- https://www.openssh.com/security.html
- https://github.com/cpandya2909/CVE-2020-15778/
