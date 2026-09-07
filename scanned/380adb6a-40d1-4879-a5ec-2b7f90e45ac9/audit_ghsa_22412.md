# [M] Stored XSS vulnerability in Jenkins brakeman Plugin

## Summary
Severity: Medium
Advisory: GHSA-7q9r-vhg2-789w
CVE: CVE-2020-2122
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7q9r-vhg2-789w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:brakeman` — affected >=0 <0.13

## Details
brakeman Plugin 0.12 and earlier did not escape values received from parsed JSON files when rendering them, resulting in a stored cross-site scripting vulnerability.

This vulnerability can be exploited by users able to control the Brakeman post-build step input data.\n\nbrakeman Plugin 0.13 escape affected values from the parsed file as they are recorded.

This fix is only applied to newly recorded data after a fixed version of the plugin is installed; historical data may still contain unsafe values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2122
- https://github.com/jenkinsci/brakeman-plugin
- https://jenkins.io/security/advisory/2020-02-12/#SECURITY-1644
- http://www.openwall.com/lists/oss-security/2020/02/12/3
