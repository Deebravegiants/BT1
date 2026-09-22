# [M] Constrata's coordinator transit engine `ciphertextContainer.UnmarshalJSON` panics on attacker-controlled short ciphertexts

## Summary
Severity: Medium
Advisory: GHSA-3ccm-4qq2-5wrp
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-3ccm-4qq2-5wrp
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/contrast` — affected >=0 <1.21.0

## Details
## Summary

`ciphertextContainer.UnmarshalJSON` decodes the third `:`-separated component of a `vault:vX:base64...` ciphertext and then unconditionally takes a 12-byte prefix slice for the AES-GCM nonce: `c.nonce = fullCiphertext[:aesGCMNonceSize]`. If the decoded blob is shorter than 12 bytes, the slice expression panics. The panic happens before any cryptographic operation, while the JSON body of the request is still being parsed inside the request handler. Because the handler is invoked from `net/http`'s standard handler goroutine, the panic is recovered to a 500 response, but the request handler aborts mid-execution and the recovered panic appears in the Coordinator's logs. An authenticated workload that holds a valid mesh certificate for any `WorkloadSecretID` can trigger the panic at will, producing log spam, request-failure metrics, and a slow but cheap denial of service against the transit-engine endpoint.

## Details

### the panicking slice

`coordinator/internal/transitengineapi/crypto.go:64-88`:

```go
// UnmarshalJSON umarshalls a json string to a ciphertextContainer holding the version prefix,
// decoded base64 nonce and ciphertext.
func (c *ciphertextContainer) UnmarshalJSON(data []byte) error {
	var encoded string
	if err := json.Unmarshal(data, &encoded); err != nil {
		return err
	}
	// Split "vault:vX:base64" format
	parts := strings.SplitN(encoded, ":", 3)
	if len(parts) < 3 {
		return fmt.Errorf("invalid ciphertext format")
	}
	version, err := extractVersion(parts[1])
	if err != nil {
		return fmt.Errorf("ciphertext version: %w", err)
	}
	c.keyVersion = version
	fullCiphertext, err := base64.StdEncoding.DecodeString(parts[2])
	if err != nil {
		return fmt.Errorf("decoding ciphertext: %w", err)
	}
	c.nonce = fullCiphertext[:aesGCMNonceSize]      // PANIC when len(fullCiphertext) < 12
	c.ciphertext = fullCiphertext[aesGCMNonceSize:]
	return nil
}
```

`aesGCMNonceSize = 12` (defined at line 33). There is no length check on `fullCiphertext`. If `parts[2]` decodes to fewer than 12 bytes (which happens for any base64 string shorter than ~16 characters), the slice expression `fullCiphertext[:aesGCMNonceSize]` triggers Go's runtime panic `runtime error: slice bounds out of range [:12] with length N`.

`UnmarshalJSON` is reached from `parseRequest`:

```go
// coordinator/internal/transitengineapi/transitengineapi.go:292-302
func parseRequest(r *http.Request, into any) error {
	defer r.Body.Close()
	if err := validateContentType(r); err != nil {
		return err
	}
	if err := json.NewDecoder(r.Body).Decode(into); err != nil {
		return err
	}
	return nil
}
```

which is called inside `getDecryptHandler` (line 178-237) before any other processing.

### auth requirement is real but trivial to satisfy for any registered workload

The transit-engine HTTP server (`transitengineapi.go:74-100`) configures `tls.RequireAndVerifyClientCert` with the Coordinator's mesh CA pool. The handler is wrapped by `authorizationMiddleware` (line 348-357) which calls `authorizeWorkloadSecret` (line 241-254). That function reads the `WorkloadSecretOID` extension from the peer cert and requires it to match the URL path's `{name}` segment.

Any workload that has gone through the normal initializer / meshapi flow (`coordinator/internal/meshapi/meshapi.go:71-119`) and has a non-empty `WorkloadSecretID` in its `PolicyEntry` is issued a mesh cert with the matching extension, so the path-name authorisation is automatically satisfied for whichever `workloadSecretID` the manifest assigned to that workload. There is no rate limiting, no proof-of-work, and no audit log on triggering the panic.

### what happens after the panic

`net/http` wraps each handler in a recovered goroutine, so the panic does not crash the Coordinator process. Instead:

1. The Go runtime captures the panic, logs `http: panic serving <peer>: runtime error: slice bounds out of range` to stderr together with a goroutine stack trace.
2. The connection is hung up without a response body (`http.Server.serve` calls `c.close()` in the recovery path).
3. The grpc-prometheus / handler metrics (registered via `promRegistry`) record the request as failed.
4. The recovered panic appears in the Coordinator's logs / journald, creating noise that an operator monitoring a real attack would have to filter out.

A workload that wants to amplify the impact can:

* Loop the request to fill the journal with stack traces (cheap operation per request, expensive log volume).
* Combine with a second valid workload identity to bypass any per-cert rate limiting added later.
* Use the panic stack trace (which contains internal source paths) as a fingerprint to determine the exact Coordinator version in lieu of a `/version` endpoint.

The panic also avoids returning a JSON error body to the caller, so callers that depend on a structured error are forced into a less informative failure mode (HTTP-level connection close).

## PoC

The bug is deterministic. Drop the following test into `coordinator/internal/transitengineapi/crypto_test.go`:

```go
func TestCiphertextContainer_UnmarshalJSON_ShortBlobPanics(t *testing.T) {
	// "AAAA" base64-decodes to 3 bytes, well under aesGCMNonceSize=12.
	body := []byte(`"vault:v1:AAAA"`)
	defer func() {
		if r := recover(); r == nil {
			t.Fatalf("expected panic, got nil")
		}
	}()
	var c ciphertextContainer
	_ = c.UnmarshalJSON(body) // panics: slice bounds out of range [:12] with length 3
}
```

End-to-end against a running Coordinator (omitted for static review; would require a Contrast cluster and a mesh-certificate-holding workload):

```bash
$ curl -k --cert workload.crt --key workload.key \
    -H 'Content-Type: application/json' \
    -d '{"ciphertext":"vault:v1:AAAA","associated_data":""}' \
    https://coordinator:8200/v1/transit/decrypt/<my-workload-secret-id>

# Connection: closed without HTTP response body.
# Coordinator log:
# http: panic serving 10.0.0.5:54321: runtime error: slice bounds out of range [:12] with length 3
# goroutine 4711 [running]:
# net/http.(*conn).serve.func1(...)
#         net/http/server.go:1883 +0xb0
# panic({0x...?, 0x...?})
#         runtime/panic.go:770 +0x132
# github.com/edgelesssys/contrast/coordinator/internal/transitengineapi.(*ciphertextContainer).UnmarshalJSON(...)
#         coordinator/internal/transitengineapi/crypto.go:85 +0x...
```

## Impact

* **Soft denial of service** against the transit-engine endpoint per workload identity. The Coordinator process survives because of `net/http`'s panic recovery, but each panicked request consumes CPU for the recovery / stack dump and floods the operator's logs.
* **Information disclosure via stack trace** in the Coordinator log. The trace pins the Coordinator binary version, the build path of the `transitengineapi` package, and exact line numbers of internal source. This is a low-grade fingerprint, but it is leaked even to operators who would normally only see the binary version through controlled means.
* **Loss of structured error reporting**: legitimate decrypt requests sharing the panicked log lines may be harder to attribute, and the API consumer sees a connection-close instead of a 4xx response, masking the cause.

CVSS rationale: `AV:N`, `AC:L`, `PR:L` (any workload with a transit-engine permission can do this), `UI:N`, `S:U`, `C:N` / `I:N` / `A:L` (low availability impact: log noise + per-request CPU cost; no full DoS because Go's HTTP panic recovery keeps the process up). Score `3.1`.

## Recommended Fix

Validate the decoded length before slicing. The minimal change at `coordinator/internal/transitengineapi/crypto.go:81-87`:

```go
fullCiphertext, err := base64.StdEncoding.DecodeString(parts[2])
if err != nil {
	return fmt.Errorf("decoding ciphertext: %w", err)
}
if len(fullCiphertext) < aesGCMNonceSize {
	return fmt.Errorf("ciphertext is too short: got %d bytes, expected at least %d for the nonce", len(fullCiphertext), aesGCMNonceSize)
}
c.nonce = fullCiphertext[:aesGCMNonceSize]
c.ciphertext = fullCiphertext[aesGCMNonceSize:]
return nil
```

A defence-in-depth tightening would also reject ciphertexts with `len(fullCiphertext) <= aesGCMNonceSize` (which would yield an empty actual ciphertext that AES-GCM open would later reject anyway, but a sharper boundary fails earlier with a clearer error). Add a unit test along the lines of the PoC that asserts a clean error rather than a panic.

## References
- https://github.com/edgelesssys/contrast/security/advisories/GHSA-3ccm-4qq2-5wrp
- https://github.com/edgelesssys/contrast/commit/d6584fbff816037472034f7ad6e08cdbab1d870d
- https://github.com/edgelesssys/contrast
- https://github.com/edgelesssys/contrast/releases/tag/v1.21.0
