# [M] SSRF in Sydent due to missing validation of hostnames

## Summary
Severity: Medium
Advisory: GHSA-9jhm-8m8c-c3f4
CVE: CVE-2021-29431
CWE: CWE-20, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-9jhm-8m8c-c3f4
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <2.3.0

## Details
### Impact

Sydent can be induced to send HTTP GET requests to internal systems, due to lack of parameter validation or IP address blacklisting.

It is not possible to exfiltrate data or control request headers, but it might be possible to use the attack to perform an internal port enumeration.

### Patches

Fixed in 9e57334, 8936925, 3d531ed, 0f00412

### Workarounds

A potential workaround would be to use a firewall to ensure that Sydent cannot reach internal HTTP resources.

### For more information

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/sydent/security/advisories/GHSA-9jhm-8m8c-c3f4
- https://nvd.nist.gov/vuln/detail/CVE-2021-29431
- https://github.com/matrix-org/sydent/commit/0f00412017f25619bc36c264b29ea96808bf310a
- https://github.com/matrix-org/sydent/commit/3d531ed50d2fd41ac387f36d44d3fb2c62dd22d3
- https://github.com/matrix-org/sydent/commit/8936925f561b0c352c2fa922d5097d7245aad00a
- https://github.com/matrix-org/sydent/commit/9e573348d81df8191bbe8c266c01999c9d57cd5f
- https://github.com/matrix-org/sydent
- https://github.com/matrix-org/sydent/releases/tag/v2.3.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-sydent/PYSEC-2021-22.yaml
- https://pypi.org/project/matrix-sydent
