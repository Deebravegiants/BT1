# [M] ECS Publisher Plugin stored and displayed API token in plain text

## Summary
Severity: Medium
Advisory: GHSA-ffj8-w4rj-vr7v
CVE: CVE-2019-1003045
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ffj8-w4rj-vr7v
Type: github-advisory

## Affected
- Maven: `de.eacg:ecs-publisher` — affected >=0 <1.0.1

## Details
A vulnerability in Jenkins ECS Publisher Plugin 1.0.0 and earlier allows attackers with Item/Extended Read permission, or local file system access to the Jenkins home directory to obtain the API token configured in this plugin's configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1003045
- https://jenkins.io/security/advisory/2019-03-25/#SECURITY-846
- http://www.openwall.com/lists/oss-security/2019/03/28/2
- http://www.securityfocus.com/bid/107628
