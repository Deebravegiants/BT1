# [M] Rundeck Community Edition vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-4262-wr7p-gpcj
CVE: CVE-2019-6804
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4262-wr7p-gpcj
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeck` — affected >=0 <3.0.13

## Details
An XSS issue was discovered on the Job Edit page in Rundeck Community Edition before 3.0.13, related to assets/javascripts/workflowStepEditorKO.js and views/execution/_wfitemEdit.gsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-6804
- https://github.com/rundeck/rundeck/issues/4406
- https://github.com/rundeck/rundeck/commit/e992e94bba22d9fca3a669f0d02c85b80a19f848
- https://docs.rundeck.com/docs/history/version-3.0.13.html
- https://github.com/rundeck/rundeck
- https://www.exploit-db.com/exploits/46251
