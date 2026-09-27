# [M] Internationalized Domain Names in Applications (IDNA): Specially crafted inputs to idna.encode() can bypass CVE-2024-3651 fix

## Summary
Severity: Medium
Advisory: GHSA-65pc-fj4g-8rjx
CVE: CVE-2026-45409
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-65pc-fj4g-8rjx
Type: github-advisory

## Affected
- PyPI: `idna` — affected >=0 <3.15

## Details
This is the same issue as CVE-2024-3651, however the original remediation in 2024 was not a complete fix. Payloads such as `"\u0660" * N` or `"\u30fb" * N + "\u6f22"` utilize the `valid_contexto` function prior to length rejection, and for high values of `N` will take a long time to process.

### Impact
A specially crafted argument to the `idna.encode()` function could consume significant resources. This may lead to a denial-of-service.

### Patches
Starting in version 3.14, the function rejects long inputs as soon as practicable prior to any further processing to minimize resource consumption. In version 3.15, this approach was extended to lesser used alternate functions (i.e. per-label conversions and codec support).

### Workarounds
Domain names cannot exceed 253 characters in length, if this length limit is enforced prior to passing the domain to the `idna.encode()` function it should no longer consume significant resources. This is triggered by arbitrarily large inputs that would not occur in normal usage, but may be passed to the library assuming there is no preliminary input validation by the higher-level application.

## References
- https://github.com/kjd/idna/security/advisories/GHSA-65pc-fj4g-8rjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45409
- https://github.com/kjd/idna
- https://github.com/pypa/advisory-database/tree/main/vulns/idna/PYSEC-2026-215.yaml
