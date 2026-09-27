# [M] API Platform Core can leak exceptions message that may contain sensitive information

## Summary
Severity: Medium
Advisory: GHSA-rfw5-cqjj-7v9r
CVE: CVE-2023-47639
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-03
Source: https://github.com/advisories/GHSA-rfw5-cqjj-7v9r
Type: github-advisory

## Affected
- Packagist: `api-platform/core` — affected >=3.2.0 <3.2.5

## Details
### Summary

Exception messages, that are not HTTP exceptions, are visible in the JSON error response.

### Details

While we wanted to make our errors compatible with the [JSON Problem](https://datatracker.ietf.org/doc/html/rfc7807) specification, we ended up handling more exceptions then we did previously (introduced at https://github.com/api-platform/core/pull/5823). Instead of leaving that to Symfony, we ended up serializing errors with our normalizers which lead to not hiding the exception details. Note that the trace is hidden in production but the message is not, and the message can contain sensitive information.

### PoC

At https://github.com/ili101/api-platform/tree/test3.2 it triggers an authentication exception as LDAP is not reachable. You can find the message available as a JSON response when trying to reach an endpoint.

### Impact

Version 3.2 until 3.2.4 is impacted.

## References
- https://github.com/api-platform/core/security/advisories/GHSA-rfw5-cqjj-7v9r
- https://nvd.nist.gov/vuln/detail/CVE-2023-47639
- https://github.com/api-platform/core/pull/5823
- https://github.com/api-platform/core/commit/ba8a7e6538bccebf14c228e43a9339214c4d9201
- https://github.com/api-platform/core
