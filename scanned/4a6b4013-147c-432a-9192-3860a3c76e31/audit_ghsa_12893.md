# [M] Reflected XSS in Gotify's /docs via import of outdated Swagger UI

## Summary
Severity: Medium
Advisory: GHSA-3244-8mff-w398
CWE: CWE-79
Ecosystem: Go
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-3244-8mff-w398
Type: github-advisory

## Affected
- Go: `github.com/gotify/server` — affected >=0 <2.2.3

## Details
### Impact

Gotify exposes an outdated instance of the [Swagger UI](https://swagger.io/tools/swagger-ui/) API documentation frontend at `/docs` which is susceptible to reflected XSS attacks when loading external Swagger config files.

Specifically, the DOMPurify version included with this version of Swagger UI is vulnerable to a [rendering XSS](https://www.vidocsecurity.com/blog/hacking-swagger-ui-from-xss-to-account-takeovers/) incorporating the mutation payload detailed in [CVE-2020-26870](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/) which was patched in 2021. This is further tracked in the GitHub Advisory Database as GHSA-QRMM-W75W-3WPX.

An attacker can execute arbitrary JavaScript and potentially take over the account of the user that clicked the link. Keep in mind, the Gotify UI won't natively expose such a malicious link, so an attacker has to get the user to open the malicious link in a context outside of Gotify.

### Patches

The vulnerability has been fixed in version 2.2.3.

### References

https://github.com/gotify/server/pull/541

## References
- https://github.com/gotify/server/security/advisories/GHSA-3244-8mff-w398
- https://github.com/gotify/server/pull/541
- https://github.com/gotify/server
- https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass
- https://www.vidocsecurity.com/blog/hacking-swagger-ui-from-xss-to-account-takeovers
