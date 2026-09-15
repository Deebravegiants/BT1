# [C] Arbitrary expression injection in Pillow

## Summary
Severity: Critical
Advisory: GHSA-8vj2-vxx3-667w
CVE: CVE-2022-22817
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-8vj2-vxx3-667w
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <9.0.1

## Details
`PIL.ImageMath.eval` in Pillow before 9.0.0 allows evaluation of arbitrary expressions, such as ones that use the Python exec method `ImageMath.eval("exec(exit())")`.

While Pillow 9.0.0 restricted top-level builtins available to PIL.ImageMath.eval(), it did not prevent builtins available to lambda expressions. These are now also restricted in 9.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-22817
- https://github.com/python-pillow/Pillow/commit/8531b01d6cdf0b70f256f93092caa2a5d91afc11
- https://github.com/advisories/GHSA-8vj2-vxx3-667w
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2022-10.yaml
- https://github.com/python-pillow/Pillow
- https://lists.debian.org/debian-lts-announce/2022/01/msg00018.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00021.html
- https://pillow.readthedocs.io/en/stable/releasenotes/9.0.0.html#restrict-builtins-available-to-imagemath-eval
- https://pillow.readthedocs.io/en/stable/releasenotes/9.0.1.html#security
- https://security.gentoo.org/glsa/202211-10
- https://www.debian.org/security/2022/dsa-5053
