# [C] Misuse of ServerConfig.PublicKeyCallback may cause authorization bypass in golang.org/x/crypto

## Summary
Severity: Critical
Advisory: GHSA-v778-237x-gjrc
CVE: CVE-2024-45337
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-v778-237x-gjrc
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.31.0

## Details
Applications and libraries which misuse the ServerConfig.PublicKeyCallback callback may be susceptible to an authorization bypass.

The documentation for ServerConfig.PublicKeyCallback says that "A call to this function does not guarantee that the key offered is in fact used to authenticate." Specifically, the SSH protocol allows clients to inquire about whether a public key is acceptable before proving control of the corresponding private key. PublicKeyCallback may be called with multiple keys, and the order in which the keys were provided cannot be used to infer which key the client successfully authenticated with, if any. Some applications, which store the key(s) passed to PublicKeyCallback (or derived information) and make security relevant determinations based on it once the connection is established, may make incorrect assumptions.

For example, an attacker may send public keys A and B, and then authenticate with A. PublicKeyCallback would be called only twice, first with A and then with B. A vulnerable application may then make authorization decisions based on key B for which the attacker does not actually control the private key.

Since this API is widely misused, as a partial mitigation golang.org/x/crypto@v0.31.0 enforces the property that, when successfully authenticating via public key, the last key passed to ServerConfig.PublicKeyCallback will be the key used to authenticate the connection. PublicKeyCallback will now be called multiple times with the same key, if necessary. Note that the client may still not control the last key passed to PublicKeyCallback if the connection is then authenticated with a different method, such as PasswordCallback, KeyboardInteractiveCallback, or NoClientAuth.

Users should be using the Extensions field of the Permissions return value from the various authentication callbacks to record data associated with the authentication attempt instead of referencing external state. Once the connection is established the state corresponding to the successful authentication attempt can be retrieved via the ServerConn.Permissions field. Note that some third-party libraries misuse the Permissions type by sharing it across authentication attempts; users of third-party libraries should refer to the relevant projects for guidance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45337
- https://github.com/golang/crypto/commit/b4f1988a35dee11ec3e05d6bf3e90b695fbd8909
- https://github.com/golang/crypto
- https://go.dev/cl/635315
- https://go.dev/issue/70779
- https://groups.google.com/g/golang-announce/c/-nPEi39gI4Q/m/cGVPJCqdAQAJ
- https://pkg.go.dev/vuln/GO-2024-3321
- https://security.netapp.com/advisory/ntap-20250131-0007
- http://www.openwall.com/lists/oss-security/2024/12/11/2
