# [C] Waitress has request processing race condition in HTTP pipelining with invalid first request

## Summary
Severity: Critical
Advisory: GHSA-9298-4cf8-g4wj
CVE: CVE-2024-49768
CWE: CWE-367, CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-29
Source: https://github.com/advisories/GHSA-9298-4cf8-g4wj
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=2.0.0 <3.0.1

## Details
### Impact

A remote client may send a request that is exactly `recv_bytes` (defaults to 8192) long, followed by a secondary request using HTTP pipelining.

When request lookahead is disabled (default) we won't read any more requests, and when the first request fails due to a parsing error, we simply close the connection.

However when request lookahead is enabled, it is possible to process and receive the first request, start sending the error message back to the client while we read the next request and queue it. This will allow the secondary request to be serviced by the worker thread while the connection should be closed.

### Patches

Waitress 3.0.1 fixes the race condition.

### Workarounds

Disable  `channel_request_lookahead`, this is set to `0` by default disabling this feature. For this vulnerability this value is required to be changed from the default.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: [pylons-project-security@googlegroups.com](mailto:pylons-project-security@googlegroups.com) (if security related)

### Thanks

- m4yfly and urn1ce From TianGong Team of Legendsec at Qi'anxin Group.

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-9298-4cf8-g4wj
- https://nvd.nist.gov/vuln/detail/CVE-2024-49768
- https://github.com/Pylons/waitress/commit/e4359018537af376cf24bd13616d861e2fb76f65
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2024-210.yaml
