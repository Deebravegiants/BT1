# [H] gosaml2 CBC Padding Panic — Unauthenticated Process Crash

## Summary
Severity: High
Advisory: GHSA-hwqm-qvj9-4jr2
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-hwqm-qvj9-4jr2
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.11.0

## Details
## Summary

The AES-CBC decryption path in `DecryptBytes()` panics on crafted ciphertext whose plaintext is all zero bytes. After decryption, `bytes.TrimRight(data, "\x00")` empties the slice, then `data[len(data)-1]` panics with `index out of range [-1]`. There is no `recover()` in the library. The panic propagates through `ValidateEncodedResponse` and kills the goroutine (or the entire process in non-`net/http` servers). An attacker needs only the SP's public RSA key (published in SAML metadata) to construct the payload — no valid signature is required.

## Affected Version

All versions of `github.com/russellhaering/gosaml2` through latest (`v0.9.0` and HEAD) that support AES-CBC encrypted assertions.

## Vulnerable Code

**`types/encrypted_assertion.go:65-79`** — `DecryptBytes`, AES-CBC branch:

```go
case MethodAES128CBC, MethodAES256CBC, MethodTripleDESCBC:
    if len(data)%k.BlockSize() != 0 {
        return nil, fmt.Errorf("encrypted data is not a multiple of the expected CBC block size %d: actual size %d", k.BlockSize(), len(data))
    }
    nonce, data := data[:k.BlockSize()], data[k.BlockSize():]
    c := cipher.NewCBCDecrypter(k, nonce)
    c.CryptBlocks(data, data)

    // Remove zero bytes
    data = bytes.TrimRight(data, "\x00")      // <-- empties the slice if plaintext is all zeros

    // Calculate index to remove based on padding
    padLength := data[len(data)-1]             // <-- PANIC: index out of range [-1]
    lastGoodIndex := len(data) - int(padLength)
    return data[:lastGoodIndex], nil
```

## Attack Details

| Property | Value |
|---|---|
| **Attack Vector** | Network (unauthenticated HTTP POST to ACS endpoint) |
| **Authentication Required** | None |
| **Attacker Knowledge** | SP's public RSA certificate (published in SAML metadata) |
| **Signature Required** | No — decryption happens before assertion signature validation |
| **Payload Size** | Single HTTP POST (~2 KB) |
| **Repeatability** | Unlimited — attacker can send the payload repeatedly |
| **Affected Configurations** | Any SP with `SPKeyStore` configured (encrypted assertion support) |
| **Trigger Condition** | AES-CBC plaintext that is all `0x00` bytes after decryption |

## Impact

- **Process crash**: In gRPC servers, custom frameworks, CLI tools, and background workers, the unrecovered panic kills the entire OS process immediately.
- **Goroutine crash**: In `net/http` servers, the built-in per-goroutine recovery catches the panic, returning HTTP 500 and logging the full stack trace. The server survives but the request-handling goroutine is terminated abnormally.
- **Denial of service**: The attack is unauthenticated and repeatable. A single crafted HTTP request is sufficient. Automated retries can keep the service down indefinitely.
- **No valid signature needed**: The SAML Response does not need to be signed. On the unsigned-response code path (`decode_response.go:346`), `decryptAssertions()` is called **before** any assertion signature validation.

## Reproduction

### Prerequisites

- Docker (for the vulnerable server)
- Python 3.8+ with `cryptography` and `requests` packages

### Files

| File | Description |
|---|---|
| `server.go` | Minimal SAML SP using gosaml2 — the victim |
| `poc.py` | Attacker script — builds and sends the crafted payload |
| `Dockerfile` | Multi-stage build for the vulnerable server |
| `run.sh` | Build and orchestration script |

### Steps

```bash
# 1. Build the vulnerable server
./run.sh build

# 2. Start the server
./run.sh start

# 3. Run the attacker script
pip install cryptography requests
./run.sh attack

# Or do everything in one command:
./run.sh all
```

### Expected Output

**Attacker terminal (`poc.py`):**

```
 ========================================================
  CVE: CBC Padding Panic — Unauthenticated Process Crash
  Target: gosaml2 (github.com/russellhaering/gosaml2)
  File:   types/encrypted_assertion.go:77
  Impact: Remote DoS — single HTTP request kills process
 ========================================================

[*] Target: http://localhost:9999
[*] Checking server health...
[+] Server is alive

========================================================
  Phase 1: Obtain SP public certificate from metadata
========================================================
[*] GET http://localhost:9999/metadata
[+] Retrieved SP certificate (xxx bytes)

========================================================
  Phase 2: Build crafted EncryptedAssertion payload
========================================================
[+] Extracted RSA public key (size=2048 bits)
[*] Generated AES-128 key: <hex>
[+] RSA-OAEP encrypted AES key (256 bytes)
[+] AES-128-CBC ciphertext: IV(<hex>) + 16 bytes
[*] Plaintext is all zeros — will trigger empty-slice panic after TrimRight
[+] Built SAML Response (xxx bytes XML, xxx bytes b64)

========================================================
  Phase 3: Send payload to /acs
========================================================
[*] POST http://localhost:9999/acs
[*] The server will decrypt our ciphertext, hit the all-zero
    plaintext edge case, and panic in DecryptBytes()...

[*] Got HTTP 500 — goroutine panicked but net/http recovered it

========================================================
  Phase 4: Verify server status
========================================================
[*] Server is still responding (net/http recovered the goroutine panic)
[*] But the panic stack trace in server logs confirms the vulnerability.
[*] In non-HTTP servers, the process would be dead.

========================================================
  VULNERABILITY CONFIRMED
  types/encrypted_assertion.go:77 — index out of range [-1]

  Stack trace:
    types/encrypted_assertion.go:77  (padLength := data[len(data)-1])
    decode_response.go:176           (decryptAssertions)
    decode_response.go:346           (ValidateEncodedResponse)
========================================================
```

**Server logs (panic stack trace):**

```
http: panic serving 127.0.0.1:xxxxx: runtime error: index out of range [-1]
goroutine XX [running]:
net/http.(*conn).serve.func1()
    /usr/local/go/src/net/http/server.go:1898 +0xbe
github.com/russellhaering/gosaml2/types.(*EncryptedAssertion).DecryptBytes(...)
    types/encrypted_assertion.go:77 +0x...
github.com/russellhaering/gosaml2.(*SAMLServiceProvider).decryptAssertions.func1(...)
    decode_response.go:176 +0x...
github.com/russellhaering/gosaml2.(*SAMLServiceProvider).decryptAssertions(...)
    decode_response.go:196 +0x...
github.com/russellhaering/gosaml2.(*SAMLServiceProvider).ValidateEncodedResponse(...)
    decode_response.go:346 +0x...
```

## Suggested Fix

Replace the unsafe zero-byte trimming and unchecked index with proper PKCS#7 unpadding and bounds checks:

```go
case MethodAES128CBC, MethodAES256CBC, MethodTripleDESCBC:
    if len(data)%k.BlockSize() != 0 {
        return nil, fmt.Errorf("ciphertext not multiple of block size")
    }
    nonce, data := data[:k.BlockSize()], data[k.BlockSize():]
    c := cipher.NewCBCDecrypter(k, nonce)
    c.CryptBlocks(data, data)

    // Validate decrypted data is non-empty
    if len(data) == 0 {
        return nil, fmt.Errorf("decrypted data is empty")
    }

    // Proper PKCS#7 unpadding with bounds checks
    padLength := int(data[len(data)-1])
    if padLength < 1 || padLength > k.BlockSize() || padLength > len(data) {
        return nil, fmt.Errorf("invalid padding length: %d", padLength)
    }

    // Verify all padding bytes are consistent
    for i := len(data) - padLength; i < len(data); i++ {
        if data[i] != byte(padLength) {
            return nil, fmt.Errorf("invalid PKCS#7 padding")
        }
    }

    return data[:len(data)-padLength], nil
```

Key changes:
1. **Remove `bytes.TrimRight(data, "\x00")`** entirely — it corrupts valid PKCS#7-padded data and creates the empty-slice condition.
2. **Bounds-check `padLength`** before using it as a slice index.
3. **Validate all padding bytes** match (proper PKCS#7 verification).
4. **Return errors** instead of panicking on malformed input.

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-hwqm-qvj9-4jr2
- https://github.com/russellhaering/gosaml2
