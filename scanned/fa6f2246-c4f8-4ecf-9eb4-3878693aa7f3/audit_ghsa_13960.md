# [M] Stored cross site scripting in changedetection.io

## Summary
Severity: Medium
Advisory: GHSA-68wj-c2jw-5pp9
CVE: CVE-2023-24769
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-18
Source: https://github.com/advisories/GHSA-68wj-c2jw-5pp9
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.40.2

## Details
Changedetection.io before 0.40.2 was discovered to contain a stored cross-site scripting (XSS) vulnerability in the main page. This vulnerability allows attackers to execute arbitrary web scripts or HTML via a crafted payload injected into the URL parameter under the "Add a new change detection watch" function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24769
- https://github.com/dgtlmoon/changedetection.io/issues/1358
- https://github.com/dgtlmoon/changedetection.io/pull/1359
- https://github.com/dgtlmoon/changedetection.io
- https://github.com/pypa/advisory-database/tree/main/vulns/changedetection-io/PYSEC-2023-10.yaml
- https://www.edoardoottavianelli.it/CVE-2023-24769
- https://www.youtube.com/watch?v=TRTpRlkU3Hc
