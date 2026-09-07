# [M] Incorrect permission checks in Jenkins Support Core Plugin

## Summary
Severity: Medium
Advisory: GHSA-w2j3-pq63-339w
CVE: CVE-2022-45383
CWE: CWE-276, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-w2j3-pq63-339w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:support-core` — affected >=0 <1206.1208.v9b_7a_1d48db_0f

## Details
Support Core Plugin defines the permission Support/DownloadBundle that allows users without Overall/Administer permission to create and download support bundles containing a limited set of diagnostic information.

Support Core Plugin 1206.v14049fa_b_d860 and earlier does not correctly perform permission checks in several HTTP endpoints.

This allows attackers with Support/DownloadBundle permission to download a previously created support bundle containing information limited to users with Overall/Administer permission.

Support Core Plugin 1206.1208.v9b_7a_1d48db_0f deprecates the Support/DownloadBundle permission. The Overall/Administer permission is now required to download support bundles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45383
- https://github.com/jenkinsci/support-core-plugin/commit/9b7a1d48db0fdfb840ca3393e9462e687e69385b
- https://github.com/jenkinsci/support-core-plugin
- https://www.jenkins.io/security/advisory/2022-11-15/#SECURITY-2804
- http://www.openwall.com/lists/oss-security/2022/11/15/4
