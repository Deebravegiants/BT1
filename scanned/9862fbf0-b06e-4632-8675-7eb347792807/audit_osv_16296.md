# [H] CVE-2019-5010

## Summary
Severity: High
Advisory: CVE-2019-5010
Aliases: PSF-2019-8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/CVE-2019-5010
Type: osv

## Details
An exploitable denial-of-service vulnerability exists in the X509 certificate parser of Python.org Python 2.7.11 / 3.6.6. A specially crafted X509 certificate can cause a NULL pointer dereference, resulting in a denial of service. An attacker can initiate or accept TLS connections using crafted certificates to trigger this vulnerability.

## References
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://access.redhat.com/errata/RHSA-2019:3520
- https://access.redhat.com/errata/RHSA-2019:3725
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00034.html
- https://security.gentoo.org/glsa/202003-26
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0758
