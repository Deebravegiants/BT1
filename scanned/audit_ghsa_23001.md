# [C] Cloud Foundry UAA privilege escalation with user invitations

## Summary
Severity: Critical
Advisory: GHSA-jcmh-x32v-7mgf
CVE: CVE-2017-4992
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jcmh-x32v-7mgf
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=2.0.0 <2.7.4.17
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.0.0 <3.6.11
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.7.0 <3.9.13
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.10.0 <4.2.0

## Details
An issue was discovered in Cloud Foundry Foundation cf-release versions prior to v261; UAA release 2.x versions prior to v2.7.4.17, 3.6.x versions prior to v3.6.11, 3.9.x versions prior to v3.9.13, and other versions prior to v4.2.0; and UAA bosh release (uaa-release) 13.x versions prior to v13.15, 24.x versions prior to v24.10, 30.x versions prior to 30.3, and other versions prior to v37. There is privilege escalation (arbitrary password reset) with user invitations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-4992
- https://github.com/cloudfoundry/uaa/commit/1c9c6dd88266cfa7d333e5d8be1031fa31c5c939
- https://github.com/cloudfoundry/uaa/commit/3ce42a4c75828cb58287c3c7495dde3f5261f12c
- https://github.com/cloudfoundry/uaa/commit/4f942064d85454a4bcc4da04cd482d114816c14a
- https://github.com/cloudfoundry/uaa/commit/96a294013c0c9a13ef32afc49d2b759f5107dc49
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/cve-2017-4992
