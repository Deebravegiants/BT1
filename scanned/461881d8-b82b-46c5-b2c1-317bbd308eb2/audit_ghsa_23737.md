# [H] Radicale is vulnerable to timing oracles and simple bruteforce attacks

## Summary
Severity: High
Advisory: GHSA-rpv4-63g3-9x23
CVE: CVE-2017-8342
CWE: CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-rpv4-63g3-9x23
Type: github-advisory

## Affected
- PyPI: `Radicale` — affected >=0 <1.1.2
- PyPI: `Radicale` — affected >=2.0.0rc1 <2.0.0rc2

## Details
Radicale before 1.1.2 and 2.0.0rc1 is prone to timing oracles and simple brute-force attacks when using the htpasswd authentication method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8342
- https://github.com/Kozea/Radicale/commit/059ba8dec1f22ccbeab837e288b3833a099cee2d
- https://github.com/Kozea/Radicale/commit/190b1dd795f0c552a4992445a231da760211183b
- https://bugs.debian.org/861514
- https://github.com/Kozea/Radicale
- https://github.com/Kozea/Radicale/blob/1.1.2/NEWS.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/radicale/PYSEC-2017-102.yaml
- https://lists.debian.org/debian-lts-announce/2020/04/msg00019.html
