# [M] Authentication Bypass in hydra

## Summary
Severity: Medium
Advisory: GHSA-3p3g-vpw6-4w66
CVE: CVE-2020-5300
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-3p3g-vpw6-4w66
Type: github-advisory

## Affected
- Go: `github.com/ory/hydra` — affected >=0 <1.4.0

## Details
### Impact

When using client authentication method "private_key_jwt" [1], OpenId specification says the following about assertion `jti`:

> A unique identifier for the token, which can be used to prevent reuse of the token. These tokens MUST only be used once, unless conditions for reuse were negotiated between the parties

Hydra does not seem to check the uniqueness of this `jti` value. Here is me sending the same token request twice, hence with the same `jti` assertion, and getting two access tokens:

```
$ curl --insecure --location --request POST 'https://localhost/_/oauth2/token' \
   --header 'Content-Type: application/x-www-form-urlencoded' \
   --data-urlencode 'grant_type=client_credentials' \
   --data-urlencode 'client_id=c001d00d-5ecc-beef-ca4e-b00b1e54a111' \
   --data-urlencode 'scope=application openid' \
   --data-urlencode 'client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer' \
   --data-urlencode 'client_assertion=eyJhb [...] jTw'
{"access_token":"zeG0NoqOtlACl8q5J6A-TIsNegQRRUzqLZaYrQtoBZQ.VR6iUcJQYp3u_j7pwvL7YtPqGhtyQe5OhnBE2KCp5pM","expires_in":3599,"scope":"application openid","token_type":"bearer"}⏎            ~$ curl --insecure --location --request POST 'https://localhost/_/oauth2/token' \
   --header 'Content-Type: application/x-www-form-urlencoded' \
   --data-urlencode 'grant_type=client_credentials' \
   --data-urlencode 'client_id=c001d00d-5ecc-beef-ca4e-b00b1e54a111' \
   --data-urlencode 'scope=application openid' \
   --data-urlencode 'client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer' \
   --data-urlencode 'client_assertion=eyJhb [...] jTw'
{"access_token":"wOYtgCLxLXlELORrwZlmeiqqMQ4kRzV-STU2_Sollas.mwlQGCZWXN7G2IoegUe1P0Vw5iGoKrkOzOaplhMSjm4","expires_in":3599,"scope":"application openid","token_type":"bearer"}
```

### Severity

We rate the severity as medium because the following reasons make it hard to replay tokens without the patch:

- TLS protects against MITM which makes it difficult to intercept valid tokens for replay attacks
- The expiry time of the JWT gives only a short window of opportunity where it could be replayed

### Patches

This will be patched with v1.4.0+oryOS.17

### Workarounds

Two workarounds have been identified:

- Do not allow clients to use `private_key_jwt`
- Use short expiry times for the JWTs

### References

https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication

### Upstream

This issue will be resolved in the upstream repository https://github.com/ory/fosite

## References
- https://github.com/ory/hydra/security/advisories/GHSA-3p3g-vpw6-4w66
- https://nvd.nist.gov/vuln/detail/CVE-2020-5300
- https://github.com/ory/hydra/commit/700d17d3b7d507de1b1d459a7261d6fb2571ebe3
- https://github.com/ory/hydra
- https://github.com/ory/hydra/releases/tag/v1.4.0
- https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication
