# [H] OpenFGA DoS vulnerability

## Summary
Severity: High
Advisory: GHSA-hr4f-6jh8-f2vq
CVE: CVE-2023-45810
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-18
Source: https://github.com/advisories/GHSA-hr4f-6jh8-f2vq
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.3.4

## Details
## Overview
OpenFGA is vulnerable to a DoS attack. When a number of ListObjects calls are executed, in some scenarios, those calls are not releasing resources even after a response has been sent, and the service as a whole becomes unresponsive.

## Fix
Upgrade to v1.3.4. This upgrade is backwards compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-hr4f-6jh8-f2vq
- https://nvd.nist.gov/vuln/detail/CVE-2023-45810
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v1.3.4
