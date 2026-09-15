# [H] Flask-AppBuilder Has No Rate Limiting on Login AUTH DB

## Summary
Severity: High
Advisory: GHSA-9hcr-9hcv-x6pv
CVE: CVE-2023-29005
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-10
Source: https://github.com/advisories/GHSA-9hcr-9hcv-x6pv
Type: github-advisory

## Affected
- PyPI: `Flask-AppBuilder` — affected >=0 <4.3.0

## Details
### Impact
Lack of rate limiting will allow an attacker to brute-force user credentials.

### Patches
Ability to enable rate limiting on Flask-AppBuilder >=  4.3.0. Use `AUTH_RATE_LIMITED = True` and `RATELIMIT_ENABLED = True` set the limit itself by using `AUTH_RATE_LIMIT`. Will apply only to database authentication.

### Workarounds
Implement rate limiting using a reverse proxy or other strategies.

## References
- https://github.com/dpgaspar/Flask-AppBuilder/security/advisories/GHSA-9hcr-9hcv-x6pv
- https://nvd.nist.gov/vuln/detail/CVE-2023-29005
- https://github.com/dpgaspar/Flask-AppBuilder/pull/1976
- https://flask-limiter.readthedocs.io/en/stable/configuration.html
- https://github.com/dpgaspar/Flask-AppBuilder
- https://github.com/dpgaspar/Flask-AppBuilder/releases/tag/v4.3.0
