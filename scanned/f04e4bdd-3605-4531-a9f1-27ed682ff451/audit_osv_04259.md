# [M] BIT-ceph-2020-10753

## Summary
Severity: Medium
Advisory: BIT-ceph-2020-10753
Aliases: CVE-2020-10753
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2020-10753
Type: osv

## Affected
- Bitnami: `ceph` — affected >=0 <14.2.21

## Details
A flaw was found in the Red Hat Ceph Storage RadosGW (Ceph Object Gateway). The vulnerability is related to the injection of HTTP headers via a CORS ExposeHeader tag. The newline character in the ExposeHeader tag in the CORS configuration file generates a header injection in the response when the CORS request is made. Ceph versions 3.x and 4.x are vulnerable to this issue.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00062.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10753
- https://lists.debian.org/debian-lts-announce/2021/08/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FFU7LXEL2UZE565FJBTY7UGH2O7ZUBVS/
- https://nvd.nist.gov/vuln/detail/CVE-2020-10753
- https://security.gentoo.org/glsa/202105-39
- https://usn.ubuntu.com/4528-1/
