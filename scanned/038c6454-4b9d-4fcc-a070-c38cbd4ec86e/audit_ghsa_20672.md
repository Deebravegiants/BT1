# [H] sanic vulnerable to Path Traversal when using `app.static` if using encoded `%2F` URLs

## Summary
Severity: High
Advisory: GHSA-8cw9-5hmv-77w6
CVE: CVE-2022-35920
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-08-06
Source: https://github.com/advisories/GHSA-8cw9-5hmv-77w6
Type: github-advisory

## Affected
- PyPI: `sanic` — affected >=22.0.0 <22.6.1
- PyPI: `sanic` — affected >=21.0.0 <21.12.2
- PyPI: `sanic` — affected >=0 <20.12.7

## Details
### Impact
Access to lateral directories when using `app.static` if using encoded `%2F` URLs. Parent directory traversal is not impacted.

### Patches
- v20.12.7 (LTS)
- v21.12.2 (LTS)
- v22.6.1

### References
https://github.com/sanic-org/sanic/issues/2478
https://github.com/sanic-org/sanic/pull/2495

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the community forums](https://community.sanicframework.org/)
* Ping us on [the Discord server](https://discord.gg/FARQzAEMAA)

## References
- https://github.com/sanic-org/sanic/security/advisories/GHSA-8cw9-5hmv-77w6
- https://nvd.nist.gov/vuln/detail/CVE-2022-35920
- https://github.com/sanic-org/sanic/issues/2478
- https://github.com/sanic-org/sanic/pull/2495
- https://github.com/sanic-org/sanic
