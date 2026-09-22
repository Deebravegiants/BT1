# [H] BIT-pillow-2021-27921

## Summary
Severity: High
Advisory: BIT-pillow-2021-27921
Aliases: CVE-2021-27921, GHSA-f4w8-cv6p-x6r5, PYSEC-2021-40
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-pillow-2021-27921
Type: osv

## Affected
- Bitnami: `pillow` — affected >=0 <8.1.1

## Details
Pillow before 8.1.2 allows attackers to cause a denial of service (memory consumption) because the reported size of a contained image is not properly checked for a BLP container, and thus an attempted memory allocation can be very large.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S7G44Z33J4BNI2DPDROHWGVG2U7ZH5JU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TQQY6472RX4J2SUJENWDZAWKTJJGP2ML/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZTSY25UJU7NJUFHH3HWT575LT4TDFWBZ/
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html
- https://security.gentoo.org/glsa/202107-33
- https://nvd.nist.gov/vuln/detail/CVE-2021-27921
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S7G44Z33J4BNI2DPDROHWGVG2U7ZH5JU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TQQY6472RX4J2SUJENWDZAWKTJJGP2ML/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTSY25UJU7NJUFHH3HWT575LT4TDFWBZ/
- https://pillow.readthedocs.io/en/stable/releasenotes/8.1.2.html
