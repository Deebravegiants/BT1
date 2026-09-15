# [M] Improper authorization in Jenkins Embeddable Build Status Plugin bypasses ViewStatus permission requirement

## Summary
Severity: Medium
Advisory: GHSA-xxhf-xq6v-c8mj
CVE: CVE-2022-34180
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-xxhf-xq6v-c8mj
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:embeddable-build-status` — affected >=0 <2.0.4

## Details
Embeddable Build Status Plugin 2.0.3 and earlier does not correctly perform the ViewStatus permission check in the HTTP endpoint it provides for \"unprotected\" status badge access.

This allows attackers without any permissions to obtain the build status badge icon for any attacker-specified job and/or build.

Embeddable Build Status Plugin 2.0.4 requires ViewStatus permission to obtain the build status badge icon.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34180
- https://github.com/jenkinsci/embeddable-build-status-plugin/commit/402148784b3f4b029eaf47cc26ebf6b9bc636183
- https://github.com/jenkinsci/embeddable-build-status-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2794
