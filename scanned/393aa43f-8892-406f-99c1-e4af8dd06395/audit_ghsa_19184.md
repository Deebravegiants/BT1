# [M] OpenFGA Authorization Bypass

## Summary
Severity: Medium
Advisory: GHSA-g4v5-6f5p-m38j
CVE: CVE-2025-25196
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-02-19
Source: https://github.com/advisories/GHSA-g4v5-6f5p-m38j
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.8.5

## Details
Overview
OpenFGA v1.8.4 or previous (Helm chart < openfga-0.2.22, docker < v.1.8.5) are vulnerable to authorization bypass when certain Check and ListObject calls are executed.

Am I Affected?
If you are using OpenFGA v1.8.4 or previous, specifically under the following conditions, you are affected by this authorization bypass vulnerability:

- Calling Check API or ListObjects with a model that has a relation [directly assignable](https://openfga.dev/docs/concepts#what-is-a-directly-related-user-type) to both [public access](https://openfga.dev/docs/concepts#what-is-type-bound-public-access) AND [userset](https://openfga.dev/docs/concepts#what-is-a-user) with the [same type](https://openfga.dev/docs/concepts#what-is-a-type), and
- A type bound public access tuple is assigned to an object, and
- userset tuple is not assigned to the same object, and
- Check request's user field is a userset that has the same type as the type bound public access tuple's user type


Fix
Upgrade to v1.8.5. This upgrade is backwards compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-g4v5-6f5p-m38j
- https://nvd.nist.gov/vuln/detail/CVE-2025-25196
- https://github.com/openfga/openfga/commit/0aee4f47e0c642de78831ceb27bb62b116f49588
- https://github.com/openfga/openfga
