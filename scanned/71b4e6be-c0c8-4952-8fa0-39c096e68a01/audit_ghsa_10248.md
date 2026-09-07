# [C] auth: Patreon provider assigns the same local user ID to every authenticated Patreon account, enabling cross‑user impersonation

## Summary
Severity: Critical
Advisory: GHSA-f6qq-3m3h-4g42
CVE: CVE-2026-42560
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-f6qq-3m3h-4g42
Type: github-advisory

## Affected
- Go: `github.com/go-pkgz/auth` — affected >=1.18.0 <1.25.2
- Go: `github.com/go-pkgz/auth/v2` — affected >=2.0.0 <2.1.2

## Details
### Summary
The Patreon OAuth provider maps every authenticated Patreon account to the same local `user.ID`, instead of deriving a unique ID from the Patreon account returned by Patreon.

In practice, this means all Patreon-authenticated users of an application using this library are collapsed into a single local identity. Any application that trusts `token.User.ID` as the stable account key can end up mixing or fully merging unrelated Patreon users, which can lead to cross-account access, privilege confusion, and subscription-state leakage.

### Details
The bug is in the Patreon provider's user-mapping logic.

Both the root module and the `v2` module create a fresh empty `token.User{}` and then derive the Patreon ID from `userInfo.ID` before that field has been populated:

```go
mapUser: func(data UserData, bdata []byte) token.User {
    userInfo := token.User{}

    uinfoJSON := uinfo{}
    if err := json.Unmarshal(bdata, &uinfoJSON); err == nil {
        userInfo.ID = "patreon_" + token.HashID(sha1.New(), userInfo.ID)
        userInfo.Name = uinfoJSON.Data.Attributes.FullName
        userInfo.Picture = uinfoJSON.Data.Attributes.ImageURL
        ...
    }
    return userInfo
}
```

Affected locations:

- `provider/providers.go:257`
- `v2/provider/providers.go:257`

At that point, `userInfo.ID` is still the empty string, so the effective result is always:

```text
patreon_ + sha1("")
```

which is:

```text
patreon_da39a3ee5e6b4b0d3255bfef95601890afd80709
```

for every Patreon user.

The code appears to have intended to hash the Patreon user ID returned by Patreon, i.e. `uinfoJSON.Data.ID`, but instead hashes the uninitialized destination field.

Why this matters:

1. Patreon is a documented, supported provider.
2. The library documents `token.User.ID` as the hashed user ID exposed to consumers.
3. The OAuth flow stores the mapped user object in JWT claims, and middleware later injects that object into the request context verbatim, consuming handlers receive the provider's wrong user.ID as authoritative identity.

Relevant flow in `v2`:

- `v2/provider/oauth2.go:207` calls `u := p.mapUser(...)`
- `v2/provider/oauth2.go:223` stores `u` in token claims
- `v2/middleware/auth.go:154` copies `*claims.User` into request context

The existing tests already encode the broken behavior:

- `provider/providers_test.go:179`
- `provider/providers_test.go:204`
- `v2/provider/providers_test.go:179`
- `v2/provider/providers_test.go:204`

Those tests assert the constant empty-string hash value for Patreon users.

### PoC
This can be reproduced locally without contacting Patreon by exercising the provider's `mapUser` logic with two different Patreon payloads.

From the repository root, create a temporary test file:

`v2/provider/patreon_repro_test.go`

```go
package provider

import "testing"

func TestPatreonSharedIdentity(t *testing.T) {
    r := NewPatreon(Params{
        URL:     "http://example.com",
        Cid:     "cid",
        Csecret: "secret",
    })

    a := r.mapUser(UserData{}, []byte(`{
        "data": {
            "attributes": {
                "full_name": "Alice",
                "image_url": "https://example.com/alice.png"
            },
            "id": "1111111"
        }
    }`))

    b := r.mapUser(UserData{}, []byte(`{
        "data": {
            "attributes": {
                "full_name": "Bob",
                "image_url": "https://example.com/bob.png"
            },
            "id": "9999999"
        }
    }`))

    if a.ID != b.ID {
        t.Fatalf("expected IDs to collide, got %q and %q", a.ID, b.ID)
    }

    t.Logf("Alice -> %s", a.ID)
    t.Logf("Bob   -> %s", b.ID)
}
```

Then run:

```bash
cd v2
go test ./provider -run TestPatreonSharedIdentity -v
```

Expected result:

```text
Alice -> patreon_da39a3ee5e6b4b0d3255bfef95601890afd80709
Bob   -> patreon_da39a3ee5e6b4b0d3255bfef95601890afd80709
```

I also confirmed this locally with three distinct Patreon `data.id` values; all of them produced the same `patreon_da39...` identity.

You can also see the same issue reflected in the existing built-in tests, which already assert this constant Patreon ID.

### Impact
This is an authentication/identity-collision vulnerability in the Patreon provider.

Impacted users:

- applications using `github.com/go-pkgz/auth/provider.NewPatreon`
- applications using `github.com/go-pkgz/auth/v2/provider.NewPatreon`
- applications that rely on `token.User.ID` as the stable local account identifier, or use it to key roles, profiles, entitlements, subscription state, or other authorization-relevant records

Practical impact:

- all Patreon-authenticated users in the same application can collapse into the same local account
- data associated with one Patreon user may be exposed to or overwritten by another Patreon user
- Patreon-specific attributes such as `is_paid_sub` can leak across unrelated users
- if a target application grants any elevated privileges to the local account keyed by this shared Patreon ID, those privileges can effectively apply to every Patreon login


### Suggested Fix
The Patreon provider should derive the user ID from the Patreon account ID returned by Patreon, not from the uninitialized destination struct.

In both of these files:

- `provider/providers.go`
- `v2/provider/providers.go`

change:

```go
userInfo.ID = "patreon_" + token.HashID(sha1.New(), userInfo.ID)
```

to:

```go
userInfo.ID = "patreon_" + token.HashID(sha1.New(), uinfoJSON.Data.ID)
```

I would also recommend adding a regression test with at least two different Patreon `data.id` values and asserting that they produce different local IDs.

Because the current bug causes all Patreon users to share a single local ID, maintainers may also want to consider migration guidance for consumers who already have Patreon-linked local accounts created under the broken identifier.

## References
- https://github.com/go-pkgz/auth/security/advisories/GHSA-f6qq-3m3h-4g42
- https://nvd.nist.gov/vuln/detail/CVE-2026-42560
- https://github.com/go-pkgz/auth/commit/c0b15ee72a8401da83c01781c16636c521f42698
- https://github.com/go-pkgz/auth
- https://github.com/go-pkgz/auth/releases/tag/v1.25.2
- https://github.com/go-pkgz/auth/releases/tag/v2.1.2
