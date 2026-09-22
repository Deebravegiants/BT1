# [H] @cedar-policy/authorization-for-expressjs has an authorization bypass via query string manipulation

## Summary
Severity: High
Advisory: GHSA-g4w6-vmgf-xqvx
CVE: CVE-2026-49473
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-g4w6-vmgf-xqvx
Type: github-advisory

## Affected
- npm: `@cedar-policy/authorization-for-expressjs` — affected >=0 <0.3.0

## Details
### Summary
@cedar-policy/authorization-for-expressjs is an open-source Express.js middleware that integrates Cedar authorization into Express applications by mapping HTTP requests to Cedar actions and evaluating authorization policies before allowing requests to proceed. An issue exists where, under certain circumstances, the middleware matches incoming requests against Cedar action mappings using req.originalUrl, which includes the query string, while Express routes requests using only the path component.

### Impact
The middleware uses req.originalUrl to match incoming requests against Cedar action mappings. In Express, req.originalUrl includes the query string, while route matching uses only the path. This creates a divergence between what Cedar authorizes and what Express executes.

When an application defines separate actions for overlapping path prefixes with different authorization requirements (for example, GET /users for listing all users with admin-only access, and GET /users/{id} for retrieving a single user with any authenticated user access), an actor can append a query string to bypass the more restrictive policy. Sending GET /users/?x=1 causes the middleware to match against /users/{id} (with id parameter set to ?x=1) and evaluate the less restrictive action, while Express routes the request to the /users list handler. This allows inappropriate access to the more restrictive endpoint.

### Impacted versions
<= 0.2.0

### Patches
This issue has been addressed in @cedar-policy/authorization-for-expressjs version 0.3. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Validate and sanitize incoming request paths before they reach the authorization middleware. Ensure that applications do not rely solely on the middleware for authorization when defining multiple actions on overlapping path prefixes with different permission levels.

### References
If you have any questions or comments about this advisory, AWS asks that you contact AWS Security via the vulnerability reporting page or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/cedar-policy/authorization-for-expressjs/security/advisories/GHSA-g4w6-vmgf-xqvx
- https://github.com/cedar-policy/authorization-for-expressjs
- https://github.com/cedar-policy/authorization-for-expressjs/releases/tag/v0.3.0
