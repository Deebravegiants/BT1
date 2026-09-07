# [H] Jenkins MATLAB Plugin cross-site request forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-9f5g-rgcr-8grw
CVE: CVE-2023-49655
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-9f5g-rgcr-8grw
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:matlab` — affected >=0 <2.11.1

## Details
Jenkins MATLAB Plugin determines whether a user-specified directory on the Jenkins controller is the location of a MATLAB installation by parsing an XML file in that directory.

MATLAB Plugin 2.11.0 and earlier does not perform permission checks in several HTTP endpoints implementing related form validation.

Additionally, these HTTP endpoints do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Additionally, the plugin does not configure its XML parser to prevent XML external entity (XXE) attacks. This allows attackers able to create files on the Jenkins controller file system to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

MATLAB Plugin 2.11.1 configures its XML parser to prevent XML external entity (XXE) attacks.

Additionally, POST requests and Item/Configure permission are required for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49655
- https://www.jenkins.io/security/advisory/2023-11-29/#SECURITY-3193
- http://www.openwall.com/lists/oss-security/2023/11/29/1
