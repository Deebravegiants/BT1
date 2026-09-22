# [M] Private key stored in plain text by Jenkins Google Compute Engine Plugin

## Summary
Severity: Medium
Advisory: GHSA-vhxq-9mpv-gj87
CVE: CVE-2022-29052
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-vhxq-9mpv-gj87
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:google-compute-engine` — affected >=0 <4.3.9

## Details
Jenkins Google Compute Engine Plugin 4.3.8 and earlier stores private keys unencrypted in cloud agent `config.xml` files on the Jenkins controller where they can be viewed by users with Agent/Extended Read permission, or access to the Jenkins controller file system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29052
- https://github.com/jenkinsci/google-compute-engine-plugin/commit/16d2ae71a1b34c81db1d74f83c41577536e5256f
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2045
