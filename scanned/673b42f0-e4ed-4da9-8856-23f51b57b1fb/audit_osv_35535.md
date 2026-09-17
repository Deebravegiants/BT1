# [C] CVE-2026-10140

## Summary
Severity: Critical
Advisory: CVE-2026-10140
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-10140
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.0 voice mode contains improper shared-state handling that allows reuse of API clients across tenant boundaries. An authenticated attacker can manipulate cache state to cause requests from other users to be processed using incorrect upstream API credentials, leading to cross-tenant billing and accountability misattribution.

## References
- https://www.ibm.com/support/pages/node/7278209
