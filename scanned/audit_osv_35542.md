# [C] CVE-2026-10560

## Summary
Severity: Critical
Advisory: CVE-2026-10560
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-10560
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.9.6 contains a missing authentication vulnerability in /api/v1/build_public_tmp/ endpoints that allows an unauthenticated attacker to read build event data or cancel jobs using a valid job identifier, resulting in information disclosure and denial of service.

## References
- https://www.ibm.com/support/pages/node/7277996
