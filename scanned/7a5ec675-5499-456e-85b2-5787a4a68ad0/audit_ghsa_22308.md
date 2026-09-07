# [M] Plone XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-cvwc-g7fw-7xrj
CVE: CVE-2011-1340
CWE: CWE-79
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cvwc-g7fw-7xrj
Type: github-advisory

## Affected
- PyPI: `plone` — affected >=0 <2.5.3

## Details
Cross-site scripting (XSS) vulnerability in `skins/plone_templates/default_error_message.pt` in Plone before 2.5.3 allows remote attackers to inject arbitrary web script or HTML via the type_name parameter to `Members/ipa/createObject`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1340
- https://web.archive.org/web/20110816092954/http://dev.plone.org/plone/changeset/12262
- https://web.archive.org/web/20110817133423/https://dev.plone.org/plone/ticket/6110
- http://jvn.jp/en/jp/JVN41222793/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2011-000056
