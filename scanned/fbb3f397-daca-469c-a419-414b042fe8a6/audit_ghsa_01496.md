# [M] Renovate vulnerable to Azure DevOps token leakage in logs

## Summary
Severity: Medium
Advisory: GHSA-36rh-ggpr-j3gj
Ecosystem: npm
Published: 2020-09-14
Source: https://github.com/advisories/GHSA-36rh-ggpr-j3gj
Type: github-advisory

## Affected
- npm: `renovate` — affected >=19.180.0 <23.25.1

## Details
### Impact

Applies to Azure DevOps users only. The bot's token may be exposed in server or pipeline logs due to the `http.extraheader=AUTHORIZATION` parameter being logged without redaction. It is recommended that Azure DevOps users revoke their existing bot credentials and generate new ones after upgrading if there's a potential that logs have been saved to a location that others can view.

### Patches

Fixed in 

### Workarounds

Do not share Renovate logs with anyone who cannot be trusted with access to the token.

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-36rh-ggpr-j3gj
- https://github.com/renovatebot/renovate
