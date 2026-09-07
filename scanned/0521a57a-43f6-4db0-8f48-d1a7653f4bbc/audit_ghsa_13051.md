# [M] Jenkins Blue Ocean Plugin cross-site request forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g4pq-p927-7pgg
CVE: CVE-2023-40341
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-16
Source: https://github.com/advisories/GHSA-g4pq-p927-7pgg
Type: github-advisory

## Affected
- Maven: `io.jenkins.blueocean:blueocean` — affected >=0 <1.27.5.1

## Details
Jenkins Blue Ocean Plugin 1.27.5 and earlier does not require POST requests for an HTTP endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to connect to an attacker-specified URL, capturing GitHub credentials associated with an attacker-specified job.

This issue is due to an incomplete fix of SECURITY-2502.

Blue Ocean Plugin 1.27.5.1 uses the configured SCM URL, instead of a user-specified URL provided as a parameter to the HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-40341
- https://www.jenkins.io/security/advisory/2023-08-16/#SECURITY-3116
- http://www.openwall.com/lists/oss-security/2023/08/16/3
