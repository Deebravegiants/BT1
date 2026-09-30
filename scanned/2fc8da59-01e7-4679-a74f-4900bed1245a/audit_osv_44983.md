# [C] CVE-2026-9202

## Summary
Severity: Critical
Advisory: CVE-2026-9202
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-9202
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.0 allows unauthenticated attackers to create unlimited user accounts on any Langflow instance; when NEW_USER_IS_ACTIVE=true (documented deployment option), newly created accounts are immediately active and can authenticate to reach RCE endpoints, bypassing the need for AUTO_LOGIN.

## References
- https://www.ibm.com/support/pages/node/7278929
