# [H] Authorization bypass in express-jwt

## Summary
Severity: High
Advisory: GHSA-6g6m-m6h5-w9gf
CVE: CVE-2020-15084
CWE: CWE-285, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-06-30
Source: https://github.com/advisories/GHSA-6g6m-m6h5-w9gf
Type: github-advisory

## Affected
- npm: `express-jwt` — affected >=0 <6.0.0

## Details
### Overview
Versions before and including 5.3.3, we are not enforcing the **algorithms** entry to be specified in the configuration.
When **algorithms** is not specified in the configuration, with the combination of jwks-rsa, it may lead to authorization bypass. 

### Am I affected?
You are affected by this vulnerability if all of the following conditions apply:

You are using express-jwt
AND 
You do not have **algorithms**  configured in your express-jwt configuration.
AND
You are using libraries such as jwks-rsa as the **secret**. 

### How to fix that?
Specify **algorithms** in the express-jwt configuration. The following is an example of a proper configuration

``` 
const checkJwt = jwt({
  secret: jwksRsa.expressJwtSecret({
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri: `https://${DOMAIN}/.well-known/jwks.json`
  }),
  // Validate the audience and the issuer.
  audience: process.env.AUDIENCE,
  issuer: `https://${DOMAIN}/`,
  // restrict allowed algorithms
  algorithms: ['RS256']
}); 
```

### Will this update impact my users?
The fix provided in patch will not affect your users if you specified the algorithms allowed. The patch now makes **algorithms** a required configuration. 


### Credit
IST Group

## References
- https://github.com/auth0/express-jwt/security/advisories/GHSA-6g6m-m6h5-w9gf
- https://nvd.nist.gov/vuln/detail/CVE-2020-15084
- https://github.com/auth0/express-jwt/commit/7ecab5f8f0cab5297c2b863596566eb0c019cdef
