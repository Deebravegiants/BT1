# [H] Jenkins HTML Publisher Plugin has a XSS vulnerability in the legacy wrapper file

## Summary
Severity: High
Advisory: GHSA-f8h4-46xv-h7jj
CVE: CVE-2026-42524
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-f8h4-46xv-h7jj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:htmlpublisher` — affected >=0 <427.1

## Details
Jenkins HTML Publisher Plugin versoins 427 and earlier do not escape the job name and URL in the legacy wrapper file.

This results in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

HTML Publisher Plugin 427.1 escapes job name and URL when generating the legacy wrapper file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42524
- https://github.com/jenkinsci/htmlpublisher-plugin
- https://www.jenkins.io/security/advisory/2026-04-29/#SECURITY-3706
