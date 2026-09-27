# [M] Exposure of Sensitive Information to an Unauthorized Actor Jenkins Script Security Plugin

## Summary
Severity: Medium
Advisory: GHSA-r9jf-hf9x-7hrv
CVE: CVE-2017-1000505
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r9jf-hf9x-7hrv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.37

## Details
In Jenkins Script Security Plugin version 1.36 and earlier, users with the ability to configure sandboxed Groovy scripts are able to use a type coercion feature in Groovy to create new `File` objects from strings. This allowed reading arbitrary files on the Jenkins master file system. Such a type coercion is now subject to sandbox protection and considered to be a call to the `new File(String)` constructor for the purpose of in-process script approval.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000505
- https://jenkins.io/security/advisory/2017-12-11
