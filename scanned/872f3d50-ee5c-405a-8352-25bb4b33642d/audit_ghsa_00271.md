# [H] Pysaml2 does not sanitize XML responses

## Summary
Severity: High
Advisory: GHSA-c2vx-49jm-h3f6
CVE: CVE-2016-10149
CWE: CWE-611
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-16
Source: https://github.com/advisories/GHSA-c2vx-49jm-h3f6
Type: github-advisory

## Affected
- PyPI: `pysaml2` — affected >=0 <4.5.0

## Details
XML External Entity (XXE) vulnerability in PySAML2 4.4.0 and earlier allows remote attackers to read arbitrary files via a crafted SAML XML request or response.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10149
- https://github.com/rohe/pysaml2/issues/366
- https://github.com/rohe/pysaml2/pull/379
- https://github.com/rohe/pysaml2/commit/6e09a25d9b4b7aa7a506853210a9a14100b8bc9b
- https://access.redhat.com/errata/RHSA-2017:0936
- https://access.redhat.com/errata/RHSA-2017:0937
- https://access.redhat.com/errata/RHSA-2017:0938
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=850716
- https://github.com/advisories/GHSA-c2vx-49jm-h3f6
- https://github.com/pypa/advisory-database/tree/main/vulns/pysaml2/PYSEC-2017-25.yaml
- https://github.com/rohe/pysaml2
- http://www.debian.org/security/2017/dsa-3759
- http://www.openwall.com/lists/oss-security/2017/01/19/5
