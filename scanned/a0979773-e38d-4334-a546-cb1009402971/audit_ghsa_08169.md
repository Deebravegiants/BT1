# [H] Caddy: mTLS client authentication silently fails open when CA certificate file is missing or malformed

## Summary
Severity: High
Advisory: GHSA-hffm-g8v7-wrv7
CVE: CVE-2026-27586
CWE: CWE-755
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-hffm-g8v7-wrv7
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.1

## Details
### Summary

Two swallowed errors in `ClientAuthentication.provision()` cause mTLS client certificate authentication to silently fail open when a CA certificate file is missing, unreadable, or malformed. The server starts without error but accepts any client certificate signed by any system-trusted CA, completely bypassing the intended private CA trust boundary.

### Details

In `modules/caddytls/connpolicy.go`, the `provision()` method has two `return nil` statements that should be `return err`:

**Bug #1 — line 787:**
```go
ders, err := convertPEMFilesToDER(fpath)
if err != nil {
    return nil  // BUG: should be "return err"
}
```

**Bug #2 — line 800:**
```go
err := caPool.Provision(ctx)
if err != nil {
    return nil  // BUG: should be "return err"
}
```

Compare with line 811 which correctly returns the error:
```go
caRaw, err := ctx.LoadModule(clientauth, "CARaw")
if err != nil {
    return err  // CORRECT
}
```

When the error is swallowed on line 787, the chain is:

1. `TrustedCACerts` remains empty (no DER data appended from the file)
2. The `len(clientauth.TrustedCACerts) > 0` guard on line 794 is false — skipped
3. `clientauth.CARaw` is nil — line 806 returns nil
4. `clientauth.ca` remains nil — no CA pool was created
5. `provision()` returns nil — caller thinks provisioning succeeded

Then in `ConfigureTLSConfig()`:

6. `Active()` returns true because `TrustedCACertPEMFiles` is non-empty
7. Default mode is set to `RequireAndVerifyClientCert` (line 860)
8. But `clientauth.ca` is nil, so `cfg.ClientCAs` is never set (line 867 skipped)
9. Go's `crypto/tls` with `RequireAndVerifyClientCert` + nil `ClientCAs` verifies client certs against the **system root pool** instead of the intended CA

The fix is changing `return nil` to `return err` on lines 787 and 800.

### PoC

1. Configure Caddy with mTLS pointing to a nonexistent CA file:

```
{
    "apps": {
        "http": {
            "servers": {
                "srv0": {
                    "listen": [":443"],
                    "tls_connection_policies": [{
                        "client_authentication": {
                            "trusted_ca_certs_pem_files": ["/nonexistent/ca.pem"]
                        }
                    }]
                }
            }
        }
    }
}
```

2. Start Caddy — it starts without any error or warning.

3. Connect with any client certificate (even self-signed):
```bash
openssl s_client -connect localhost:443 -cert client.pem -key client-key.pem
```

4. The TLS handshake succeeds despite the certificate not being signed by the intended CA.

A full Go test that proves the bug end-to-end (including a successful TLS handshake with a random self-signed client cert) is here: https://gist.github.com/moscowchill/9566c79c76c0b64c57f8bd0716f97c48

Test output:
```
=== RUN   TestSwallowedErrorMTLSFailOpen
    BUG CONFIRMED: provision() swallowed the error from a nonexistent CA file.
    tls.Config has RequireAndVerifyClientCert but ClientCAs is nil.
    CRITICAL: TLS handshake succeeded with a self-signed client cert!
    The server accepted a client certificate NOT signed by the intended CA.
--- PASS: TestSwallowedErrorMTLSFailOpen (0.03s)
```

### Impact

Any deployment using `trusted_ca_cert_file` or `trusted_ca_certs_pem_files` for mTLS will silently degrade to accepting any system-trusted client certificate if the CA file becomes unavailable. This can happen due to a typo in the path, file rotation, corruption, or permission changes. The server gives no indication that mTLS is misconfigured.

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-hffm-g8v7-wrv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27586
- https://github.com/caddyserver/caddy/commit/d42d39b4bc237c628f9a95363b28044cb7a7fe72
- https://gist.github.com/moscowchill/9566c79c76c0b64c57f8bd0716f97c48
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.11.1
- https://pkg.go.dev/vuln/GO-2026-4539
