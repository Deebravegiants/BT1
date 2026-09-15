# [H] CVE-2020-35573

## Summary
Severity: High
Advisory: CVE-2020-35573
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-20
Source: https://osv.dev/vulnerability/CVE-2020-35573
Type: osv

## Details
srs2.c in PostSRSd before 1.10 allows remote attackers to cause a denial of service (CPU consumption) via a long timestamp tag in an SRS address.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00031.html
- https://security.gentoo.org/glsa/202107-08
- https://github.com/roehling/postsrsd/commit/4733fb11f6bec6524bb8518c5e1a699288c26bac
