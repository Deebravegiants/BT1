# [H] UAA privilege escalation across identity zones

## Summary
Severity: High
Advisory: GHSA-8v97-gv3g-32rf
CVE: CVE-2018-1262
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8v97-gv3g-32rf
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.12.0 <4.12.2
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=4.13.0 <4.13.4

## Details
Cloud Foundry Foundation UAA, versions 4.12.X and 4.13.X, introduced a feature which could allow privilege escalation across identity zones for clients performing offline validation. A zone administrator could configure their zone to issue tokens which impersonate another zone, granting up to admin privileges in the impersonated zone for clients performing offline token validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1262
- https://github.com/cloudfoundry/uaa/commit/14c745aa293b8d3ce9cdd6bfbc6c0ef3f269b21
- https://github.com/cloudfoundry/uaa/commit/dccd3962f969913996ee88f653fce3b108c0205
- https://github.com/cloudfoundry/uaa
- https://www.cloudfoundry.org/blog/cve-2018-1262
