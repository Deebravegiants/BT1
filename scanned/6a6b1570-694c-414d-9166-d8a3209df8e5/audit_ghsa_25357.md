# [M] Plone XSS in User Fullname Property and File Upload

## Summary
Severity: Medium
Advisory: GHSA-hprr-4vfq-fcxw
CVE: CVE-2021-3313
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hprr-4vfq-fcxw
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <5.2.4

## Details
Plone CMS until version 5.2.4 has a stored Cross-Site Scripting (XSS) vulnerability in the user fullname property and the file upload functionality. The user's input data is not properly encoded when being echoed back to the user. This data can be interpreted as executable code by the browser and allows an attacker to execute JavaScript in the context of the victim's browser if the victim opens a vulnerable page containing an XSS payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3313
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2021-78.yaml
- https://plone.org/download/releases/5.2.3
- https://plone.org/security/hotfix/20210518
- https://plone.org/security/hotfix/20210518/stored-xss-from-file-upload-svg-html
- https://plone.org/security/hotfix/20210518/stored-xss-from-user-fullname
- https://www.compass-security.com/fileadmin/Research/Advisories/2021-07_CSNC-2021-013_XSS_in_Plone_CMS.txt
- http://www.openwall.com/lists/oss-security/2021/05/22/1
