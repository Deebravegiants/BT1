# [H] Default Express middleware security check is ignored in production

## Summary
Severity: High
Advisory: GHSA-4j6x-w426-6rc6
Ecosystem: npm
Published: 2019-11-08
Source: https://github.com/advisories/GHSA-4j6x-w426-6rc6
Type: github-advisory

## Affected
- npm: `@cubejs-backend/api-gateway` — affected >=0.11.0 <0.11.17

## Details
## Default Express middleware security check is ignored in production

### Impact
All Cube.js deployments that use affected versions of `@cubejs-backend/api-gateway` with default express authentication middleware in production environment are affected.

### Patches
@cubejs-backend/api-gateway@0.11.17

### Workarounds
Override default authentication express middleware: https://cube.dev/docs/@cubejs-backend-server-core#options-reference-check-auth-middleware

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/cube-js/cube.js/issues
* Reach out us in community Slack: https://slack.cube.dev/

## References
- https://github.com/cube-js/cube.js/security/advisories/GHSA-4j6x-w426-6rc6
- https://github.com/advisories/GHSA-4j6x-w426-6rc6
