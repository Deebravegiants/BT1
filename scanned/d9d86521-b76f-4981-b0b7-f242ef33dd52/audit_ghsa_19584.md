# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-w222-m46c-mgh6
CVE: CVE-2025-46331
CWE: CWE-284, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-04-30
Source: https://github.com/advisories/GHSA-w222-m46c-mgh6
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=1.3.6 <1.8.11

## Details
Overview
OpenFGA v1.8.10 or previous (Helm chart <= openfga-0.2.28, docker <= v.1.8.10) are vulnerable to authorization bypass when certain Check and ListObject calls are executed.

Am I Affected?
If you are using OpenFGA v1.8.10 or previous, specifically under the following conditions, you are affected by this authorization bypass vulnerability:
- Calling Check API or ListObjects with an [authorization model](https://openfga.dev/docs/concepts#what-is-an-authorization-model) that has tuple cycle.
- [Check query cache](https://github.com/openfga/openfga/blob/9b5974458b777707ed2a30ba6303699499e655ee/.config-schema.json#L528) is enabled, and
- There are multiple check / list objects requests involving the tuple cycle within the check query TTL

Fix
Upgrade to v1.8.11. This upgrade is backwards compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-w222-m46c-mgh6
- https://nvd.nist.gov/vuln/detail/CVE-2025-46331
- https://github.com/openfga/openfga/commit/244302e7a8b979d66cc1874a3899cdff7d47862f
- https://github.com/openfga/openfga
