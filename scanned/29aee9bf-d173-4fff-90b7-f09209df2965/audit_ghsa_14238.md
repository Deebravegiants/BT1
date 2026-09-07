# [M] Jenkins Lucene-Search Plugin vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-gh5w-gffh-68pr
CVE: CVE-2023-30529
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-gh5w-gffh-68pr
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:lucene-search` — affected >=0 <398.v3dfa_cb_223984

## Details
Jenkins Lucene-Search Plugin 387.v938a_ecb_f7fe9 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to reindex the database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30529
- https://github.com/jenkinsci/lucene-search-plugin/commit/828f79fedbe3da08b17937a85b98b5d7f499a8dd
- https://github.com/jenkinsci/lucene-search-plugin/commit/ffd691642b8dda63b55cfc7e73993336554dbcb2
- https://www.jenkins.io/security/advisory/2023-04-12/#SECURITY-3013
- http://www.openwall.com/lists/oss-security/2023/04/13/3
