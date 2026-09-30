# [C] CVE-2021-21243

## Summary
Severity: Critical
Advisory: CVE-2021-21243
Aliases: GHSA-9mmq-fm8c-q4fv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21243
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, a Kubernetes REST endpoint exposes two methods that deserialize untrusted data from the request body. These endpoints do not enforce any authentication or authorization checks. This issue may lead to pre-auth RCE. This issue was fixed in 4.0.3 by not using deserialization at KubernetesResource side.

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-9mmq-fm8c-q4fv
- https://github.com/theonedev/onedev/commit/9637fc8fa461c5777282a0021c3deb1e7a48f137
