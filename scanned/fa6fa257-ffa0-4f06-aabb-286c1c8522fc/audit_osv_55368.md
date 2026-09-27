# [H] CVE-2025-40777

## Summary
Severity: High
Advisory: CVE-2025-40777
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-40777
Type: osv

## Details
If a `named` caching resolver is configured with `serve-stale-enable` `yes`, and with `stale-answer-client-timeout` set to `0` (the only allowable value other than `disabled`), and if the resolver, in the process of resolving a query, encounters a CNAME chain involving a specific combination of cached or authoritative records, the daemon will abort with an assertion failure.
This issue affects BIND 9 versions 9.20.0 through 9.20.10, 9.21.0 through 9.21.9, and 9.20.9-S1 through 9.20.10-S1.

## References
- https://kb.isc.org/docs/cve-2025-40777
