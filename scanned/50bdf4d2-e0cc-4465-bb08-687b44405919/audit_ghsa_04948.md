# [H] Spinnaker has non-safe yaml deserialization, allowing RCE when using specific types

## Summary
Severity: High
Advisory: GHSA-c8q4-9h32-2ww8
CVE: CVE-2026-44795
CWE: CWE-470, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-c8q4-9h32-2ww8
Type: github-advisory

## Affected
- Maven: `io.spinnaker.rosco:rosco-core` — affected >=0 <2025.3.3
- Maven: `io.spinnaker.orca:orca-core` — affected >=0 <2025.3.3
- Maven: `io.spinnaker.rosco:rosco-core` — affected >=2025.4.0 <2025.4.4
- Maven: `io.spinnaker.rosco:rosco-core` — affected >=2026.0.0 <2026.0.3
- Maven: `io.spinnaker.orca:orca-core` — affected >=2025.4.0 <2025.4.4
- Maven: `io.spinnaker.orca:orca-core` — affected >=2026.0.0 <2026.0.3

## Details
### Impact
There's an unsafe YAML processing vulnerability that bypasses safe deserialization. This impacts users when when performing:
* CloudFormation deployments
* CloudFoundry Baking

The usage of a non-safe constructor use allows arbitrary loading of Java classes leading to RCE.

### Patches
 2025.3.3, 2026.0.3 and 2025.4.4.

### Workarounds
Disable the CloudFormation system and cloudfoundry baking operations.

### Resources
Join Spinnaker on Slack for more information!

## References
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-c8q4-9h32-2ww8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44795
- https://github.com/spinnaker/spinnaker/commit/4cbe1d5fea9df573aadfd8b093fb4b594b354ee5
- https://github.com/spinnaker/spinnaker/commit/e57c0db4584b398473a7bbb19402ce6c1e89b627
- https://github.com/spinnaker/spinnaker/commit/f69d7b534d068ed74d0d3a1fbf17e2c945d36e5e
- https://github.com/spinnaker/spinnaker
