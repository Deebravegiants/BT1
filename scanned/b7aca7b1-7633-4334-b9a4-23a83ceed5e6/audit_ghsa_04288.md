# [M] gorest InMemorySecret2FA race condition allows process crash via concurrent map access (CWE-362)

## Summary
Severity: Medium
Advisory: GHSA-cpwg-x64r-rgwg
CVE: CVE-2026-48154
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-cpwg-x64r-rgwg
Type: github-advisory

## Affected
- Go: `github.com/pilinux/gorest` — affected >=0 <1.12.2

## Details
## Vulnerability: CWE-362 — Concurrent Map Access Race Condition in InMemorySecret2FA

**CWE:** CWE-362 (Concurrent Execution using Shared Resource with Improper Synchronization)

### Affected Component
- `github.com/pilinux/gorest` — Go REST API boilerplate
- InMemorySecret2FA — in-memory 2FA secret store

### Vulnerability Locations

| File | Line | Role |
|------|------|------|
| `database/model/twoFA.go` | 43 | Global `map[uint64]Secret2FA` — bare map, no sync.RWMutex |
| `handler/login.go` | 139 | Map write during user login |
| `handler/twoFA.go` | 205 | Map write during 2FA setup |
| `handler/twoFA.go` | 272 | Map write during 2FA activation |
| `handler/twoFA.go` | 575 | Map write during 2FA verification |
| `handler/twoFA.go` | 189 | Map read during 2FA operations |
| `handler/twoFA.go` | 245 | Map read during 2FA operations |
| `handler/twoFA.go` | 491 | Map read during 2FA operations |
| `service/common.go` | 79 | Map delete |

### Data Flow

```
Multiple HTTP goroutines (concurrent requests)
    │
    ├── handler/login.go:139 ─► map write ──┐
    ├── handler/twoFA.go:205 ─► map write ──┼── InMemorySecret2FA (bare map)
    ├── handler/twoFA.go:189 ─► map read ───┤      ▲  NO sync.RWMutex
    ├── handler/twoFA.go:245 ─► map read ───┤      │
    ├── handler/twoFA.go:491 ─► map read ───┤      │
    └── service/common.go:79 ─► map delete ─┘      │
                                                   │
            Go runtime detects concurrent map      │
            read+write or write+write              │
                │                                  │
                ▼                                  │
    fatal error: concurrent map read and map write │
    fatal error: concurrent map writes             │
                │                                  │
                ▼                                  │
         Process crash (DoS) ──────────────────────┘
```

### Description

The `InMemorySecret2FA` in `database/model/twoFA.go` was defined as a package-level `map[uint64]Secret2FA` — a bare Go map with no synchronization primitive. Multiple HTTP handlers in `handler/login.go` and `handler/twoFA.go` read from and wrote to this map concurrently. Go's runtime detects unsynchronized concurrent map access and throws an unrecoverable `fatal error`, which crashes the entire process.

This is a CWE-362 race condition: the shared resource (the map) is accessed concurrently without proper synchronization, and the failure mode is a hard process crash (denial of service).

### Trigger Conditions

1. Two users with 2FA enabled logging in simultaneously — concurrent map writes
2. One user logging in (map write) while another performs 2FA verification (map read)
3. Any concurrent combination of the 9 affected handler locations

### Proof of Concept

```bash
# Simulate two concurrent logins with 2FA enabled
for i in 1 2; do
    curl -X POST http://target:8080/api/v1/login         -H "Content-Type: application/json"         -d "{"email":"user${i}@example.com","password":"testpass"}" &
done
wait

# Go runtime output:
# fatal error: concurrent map writes
# goroutine 34 [running]:
# runtime.throw({0x...})
#   runtime/map.go:...
```

### Impact

- **Availability (High):** Hard process crash via Go runtime fatal error. No recovery possible — the process exits. An attacker can repeat the concurrent requests to crash the service on demand.
- **Confidentiality (None):** The crash itself does not leak data.
- **Integrity (None):** No data corruption (Go prevents it by crashing).

### Fix (PR #391)

Introduced `Secret2FAStore` struct with `sync.RWMutex` protection:

```go
// BEFORE: database/model/twoFA.go — bare map, no protection
var InMemorySecret2FA map[uint64]Secret2FA

// AFTER: Wrapped with sync.RWMutex
type Secret2FAStore struct {
    mu   sync.RWMutex
    data map[uint64]Secret2FA
}

func (s *Secret2FAStore) Get(key uint64) (Secret2FA, bool) {
    s.mu.RLock()
    defer s.mu.RUnlock()
    v, ok := s.data[key]
    return cloneSecret2FA(v), ok
}

func (s *Secret2FAStore) Set(key uint64, value Secret2FA) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.data[key] = cloneSecret2FA(value)
}

func (s *Secret2FAStore) Delete(key uint64) {
    s.mu.Lock()
    defer s.mu.Unlock()
    delete(s.data, key)
}

// cloneSecret2FA returns a deep copy of a Secret2FA.
// This prevents external code from mutating the store's data
// through shared slice backing arrays.
func cloneSecret2FA(v Secret2FA) Secret2FA {
	out := Secret2FA{Image: v.Image}
	if v.PassHash != nil {
		out.PassHash = append([]byte(nil), v.PassHash...)
	}
	if v.KeySalt != nil {
		out.KeySalt = append([]byte(nil), v.KeySalt...)
	}
	if v.Secret != nil {
		out.Secret = append([]byte(nil), v.Secret...)
	}
	return out
}
```

All 9 handler call sites updated from direct map access to store method calls.

### Not Vulnerable (verified during audit)

- JWT: RSA keys from files, appleboy/gin-jwt middleware — correct
- Password hashing: Argon2 via pilinux/argon2 — correct
- SQL queries: GORM parameterized — correct
- CORS: validates wildcard+credentials combination at config load — correct

### Patched Versions

All versions after PR #391 merge.

### Resources

- Fix PR: https://github.com/pilinux/gorest/pull/391

### Credit

Reported by @saaa99999999 via manual security audit.

## References
- https://github.com/pilinux/gorest/security/advisories/GHSA-cpwg-x64r-rgwg
- https://github.com/pilinux/gorest/pull/391
- https://github.com/pilinux/gorest
