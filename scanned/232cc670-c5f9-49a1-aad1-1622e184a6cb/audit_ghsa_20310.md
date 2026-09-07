# [H] Cross-site Scripting in Jenkins NS-ND Integration Performance Publisher Plugin

## Summary
Severity: High
Advisory: GHSA-pv38-mqpp-v72h
CVE: CVE-2022-34191
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-pv38-mqpp-v72h
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:cavisson-ns-nd-integration` — affected >=0 <4.8.0.129

## Details
Jenkins NS-ND Integration Performance Publisher Plugin 4.8.0.77 and earlier does not escape the name of NetStorm Test parameters on views displaying parameters, resulting in a stored cross-site scripting (XSS) vulnerability exploitable by attackers with Item/Configure permission.

Exploitation of this vulnerability requires that parameters are listed on another page, like the \"Build With Parameters\" and \"Parameters\" pages provided by Jenkins (core), and that those pages are not hardened to prevent exploitation. Jenkins (core) has prevented exploitation of vulnerabilities of this kind on the \"Build With Parameters\" and \"Parameters\" pages since 2.44 and LTS 2.32.2 as part of the [SECURITY-353 / CVE-2017-2601](https://www.jenkins.io/security/advisory/2017-02-01/#persisted-cross-site-scripting-vulnerability-in-parameter-names-and-descriptions) fix. Additionally, several plugins have previously been updated to list parameters in a way that prevents exploitation by default, see [SECURITY-2617 in the 2022-04-12 security advisory for a list](https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-2617).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34191
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin/commit/5b6dc5957edc3eff1b7ef2c3b52264524161b734
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin/commit/6321f09aa9518eeeaeaa2f81182e1eae079dbdf2
- https://github.com/jenkinsci/cavisson-ns-nd-integration-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2784
