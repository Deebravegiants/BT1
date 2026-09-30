# [M] Protection Mechanism Failure in Jenkins Doktor Plugin

## Summary
Severity: Medium
Advisory: GHSA-64q9-f38h-9mwx
CVE: CVE-2022-25204
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-64q9-f38h-9mwx
Type: github-advisory

## Affected
- Maven: `by.dev.madhead.doktor:doktor` — affected >=0

## Details
Jenkins Doktor Plugin 0.4.1 and earlier implements functionality that allows agent processes to render files on the controller as Markdown or Asciidoc, and error messages allow attackers able to control agent processes to determine whether a file with a given name exists.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25204
- https://github.com/jenkinsci/doktor-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2548
