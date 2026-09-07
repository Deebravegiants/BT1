# [M] Kallithea cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fh5c-7gmg-xmp6
CVE: CVE-2015-1864
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fh5c-7gmg-xmp6
Type: github-advisory

## Affected
- PyPI: `Kallithea` — affected >=0 <0.2.1

## Details
Multiple cross-site scripting (XSS) vulnerabilities in the administration pages in Kallithea before 0.2.1 allow remote attackers to inject arbitrary web script or HTML via the (1) first name or (2) last name user details, or the (3) repository, (4) repository group, or (5) user group description.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1864
- https://github.com/msabramo/kallithea
- https://github.com/pypa/advisory-database/tree/main/vulns/kallithea/PYSEC-2017-17.yaml
- https://kallithea-scm.org/repos/kallithea/changeset/a8f2986afc18c9221bf99f88b06e60ab83c86c55
- https://kallithea-scm.org/security/cve-2015-1864.html
- https://web.archive.org/web/20200228161446/http://www.securityfocus.com/bid/74184
- http://www.openwall.com/lists/oss-security/2015/04/14/12
- http://www.securityfocus.com/bid/74184
