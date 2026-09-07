# [H] Sydent vulnerable to denial of service attack via memory exhaustion

## Summary
Severity: High
Advisory: GHSA-wmg4-8cp2-hpg9
CVE: CVE-2021-29430
CWE: CWE-20, CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-wmg4-8cp2-hpg9
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <2.3.0

## Details
### Impact

Sydent does not limit the size of requests it receives from HTTP clients. A malicious user could send an HTTP request with a very large body, leading to disk space exhaustion and denial of service.

Sydent also does not limit response size for requests it makes to remote Matrix homeservers. A malicious homeserver could return a very large response, again leading to memory exhaustion and denial of service.

This affects any server which accepts registration requests from untrusted clients.

### Patches

Patched by 89071a1, 0523511, f56eee3.

### Workarounds

Request sizes can be limited in an HTTP reverse-proxy.

There are no known workarounds for the problem with overlarge responses.

### For more information

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/sydent/security/advisories/GHSA-wmg4-8cp2-hpg9
- https://nvd.nist.gov/vuln/detail/CVE-2021-29430
- https://github.com/matrix-org/sydent/commit/0523511d2fb40f2738f8a8549868f44b96e5dab7
- https://github.com/matrix-org/sydent/commit/89071a1a754c69a50deac89e6bb74002d4cda19d
- https://github.com/matrix-org/sydent/commit/f56eee315b6c44fdd9f6aa785cc2ec744a594428
- https://github.com/matrix-org/sydent
- https://github.com/matrix-org/sydent/releases/tag/v2.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-sydent/PYSEC-2021-21.yaml
- https://pypi.org/project/matrix-sydent
