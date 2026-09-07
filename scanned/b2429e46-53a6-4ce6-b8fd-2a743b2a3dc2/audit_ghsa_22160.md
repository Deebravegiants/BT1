# [M] Cloud Foundry UAA open redirect

## Summary
Severity: Medium
Advisory: GHSA-xh4m-99qp-w483
CVE: CVE-2018-11041
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xh4m-99qp-w483
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <4.7.5
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.8.0 <4.10.1
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.11.0 <4.12.3
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.13.0 <4.19.0

## Details
Cloud Foundry UAA, versions later than 4.6.0 and prior to 4.19.0 except 4.10.1 and 4.7.5 and uaa-release versions later than v48 and prior to v60 except v55.1 and v52.9, does not validate redirect URL values on a form parameter used for internal UAA redirects on the login page, allowing open redirects. A remote attacker can craft a malicious link that, when clicked, will redirect users to arbitrary websites after a successful login attempt.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11041
- https://github.com/cloudfoundry/uaa/commit/238ce572fdaebbb8357b265d2f77eb9761199a09
- https://github.com/cloudfoundry/uaa/commit/57a15dfb7e0e3a59019ebe951793b586512b196
- https://github.com/cloudfoundry/uaa/commit/7a8f157f7e2feed2d0ebb63b163ff735b6340b9
- https://github.com/cloudfoundry/uaa/commit/7d750e036cd52c5d30e73e28cbcae23126d7154
- https://github.com/cloudfoundry/uaa/commit/83c8627c2da7845043b65e6ba354a64b4f9c6e2f
- https://github.com/cloudfoundry/uaa/commit/8a599448781acd481aa9dab1b0bde3424e00ced
- https://github.com/cloudfoundry/uaa/commit/d17b23fc3bf9b86f111774925afadfced75315c
- https://github.com/cloudfoundry/uaa/commit/f6362a8f1865314aa507fc5de772848b7e55236
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/blog/cve-2018-11041
