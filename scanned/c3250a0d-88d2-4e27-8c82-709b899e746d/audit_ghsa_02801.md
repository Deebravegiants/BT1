# [C] Buffer Overflow in Pillow

## Summary
Severity: Critical
Advisory: GHSA-7534-mm45-c74v
CVE: CVE-2021-34552
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-7534-mm45-c74v
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <8.3.0

## Details
Pillow through 8.2.0 and PIL (aka Python Imaging Library) through 1.1.7 allow an attacker to pass controlled parameters directly into a convert function to trigger a buffer overflow in Convert.c.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34552
- https://github.com/python-pillow/Pillow/pull/5567
- https://github.com/python-pillow/Pillow/commit/31c473898c29d1b7cb6555ce67d9503a4906b83f
- https://github.com/advisories/GHSA-7534-mm45-c74v
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2021-331.yaml
- https://github.com/python-pillow/Pillow
- https://lists.debian.org/debian-lts-announce/2021/07/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7V6LCG525ARIX6LX5QRYNAWVDD2MD2SV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VUGBBT63VL7G4JNOEIPDJIOC34ZFBKNJ
- https://pillow.readthedocs.io/en/stable/releasenotes/8.3.0.html#buffer-overflow
- https://pillow.readthedocs.io/en/stable/releasenotes/index.html
- https://security.gentoo.org/glsa/202211-10
