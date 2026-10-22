# [H] Cloud Foundry UAA password reset vulnerability

## Summary
Severity: High
Advisory: GHSA-cgrg-x34r-78f3
CVE: CVE-2017-4991
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cgrg-x34r-78f3
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=2.0.0 <2.7.4.16
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.6.10
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.7.0 <3.9.12
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.10.0 <3.17.0

## Details
An issue was discovered in Cloud Foundry Foundation cf-release versions prior to v260; UAA release 2.x versions prior to v2.7.4.16, 3.6.x versions prior to v3.6.10, 3.9.x versions prior to v3.9.12, and other versions prior to v3.17.0; and UAA bosh release (uaa-release) 13.x versions prior to v13.14, 24.x versions prior to v24.9, 30.x versions prior to 30.2, and other versions prior to v36. Privileged users in one zone are allowed to perform a password reset for users in a different zone.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-4991
- https://github.com/cloudfoundry/uaa/commit/2ca35f1723e039aa7d2318134b05d02e40072a18
- https://github.com/cloudfoundry/uaa/commit/ba23bcf109704ab2eae519b705d7b2a75e023553
- https://github.com/cloudfoundry/uaa/commit/bbf6751bc0d87c4a3aaf21b54e26ce328ab998b3
- https://github.com/cloudfoundry/uaa/commit/eb3f86054489039e11eabd54a8ec9a46c22abfc8
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/cve-2017-4991
