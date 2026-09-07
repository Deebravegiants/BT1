# [M] Mezzanine CMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-269j-37ww-cmh3
CVE: CVE-2025-50481
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-07-23
Source: https://github.com/advisories/GHSA-269j-37ww-cmh3
Type: github-advisory

## Affected
- PyPI: `Mezzanine` — affected >=0

## Details
A cross-site scripting (XSS) vulnerability in the component /blog/blogpost/add of Mezzanine CMS v6.1.0 allows attackers to execute arbitrary web scripts or HTML via injecting a crafted payload into a blog post.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-50481
- https://github.com/kevinpdicks/Mezzanine-CMS-6.1.0-XSS
- https://github.com/pypa/advisory-database/tree/main/vulns/mezzanine/PYSEC-2025-137.yaml
- https://github.com/stephenmcd/mezzanine
