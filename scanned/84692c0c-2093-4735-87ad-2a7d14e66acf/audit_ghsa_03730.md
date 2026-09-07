# [M] mistune Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-98gj-wwxm-cj3h
CVE: CVE-2017-16876
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-98gj-wwxm-cj3h
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <0.8.1

## Details
Cross-site scripting (XSS) vulnerability in the _keyify function in mistune.py in Mistune before 0.8.1 allows remote attackers to inject arbitrary web script or HTML by leveraging failure to escape the "key" argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16876
- https://github.com/lepture/mistune/commit/5f06d724bc05580e7f203db2d4a4905fc1127f98
- https://bugzilla.redhat.com/show_bug.cgi?id=1524596
- https://github.com/lepture/mistune
- https://github.com/lepture/mistune/blob/master/CHANGES.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/mistune/PYSEC-2017-18.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NUR3GMHQBMA3UC4PFMCK6GCLOQC4LQQC
