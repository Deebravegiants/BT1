# [M] Potential API key leak

## Summary
Severity: Medium
Advisory: GHSA-63rq-p8fp-524q
CWE: CWE-200
Ecosystem: PyPI
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-63rq-p8fp-524q
Type: github-advisory

## Affected
- PyPI: `sopel-modules.weather` — affected >=0 <1.2.4

## Details
If a user is actively blackholing the location or weather APIs, or those APIs become otherwise unavailable, it is possible for the API keys to get leaked to the active IRC channel.

This is patched in v1.2.4

## References
- https://github.com/sopel-irc/sopel-weather/security/advisories/GHSA-63rq-p8fp-524q
