# [C] Fiber Utils UUIDv4 and UUID Silent Fallback to Predictable Values

## Summary
Severity: Critical
Advisory: GHSA-m98w-cqp3-qcqr
CVE: CVE-2025-66565
CWE: CWE-252, CWE-331, CWE-338
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-m98w-cqp3-qcqr
Type: github-advisory

## Affected
- Go: `github.com/gofiber/utils/v2` — affected >=0 <2.0.0-rc.4
- Go: `github.com/gofiber/utils` — affected >=0 <1.2.0

## Details
## Summary

Critical security vulnerabilities exist in both the `UUIDv4()` and `UUID()` functions of the `github.com/gofiber/utils` package. When the system's cryptographic random number generator (`crypto/rand`) fails, both functions silently fall back to returning predictable UUID values, the zero UUID `"00000000-0000-0000-0000-000000000000"`. This compromises the security of all Fiber applications using these functions for security-critical operations on **Go versions prior to 1.24**.

**Both functions are vulnerable to the same root cause (`crypto/rand` failure):**

* `UUIDv4()`: Indirect vulnerability through `uuid.NewRandom()` → `crypto/rand.Read()` → fallback to `UUID()`
* `UUID()`: Direct vulnerability through `crypto/rand.Read(uuidSeed[:])` → silent zero UUID return

> **Note:** Go 1.24 and later panics on `crypto/rand` `Read()` failures, mitigating this vulnerability. Applications running on Go 1.24+ are not affected by the silent fallback behavior.

---

## Vulnerability Details

### Affected Functions

* **Package**: `github.com/gofiber/utils`
* **Functions**: `UUIDv4()` and `UUID()`
* **Return Type**: `string` (both functions)
* **Locations**: `common.go:93-99` (UUIDv4), `common.go:60-89` (UUID)

### Technical Description

The vulnerability occurs through two related but distinct failure paths, both ultimately caused by `crypto/rand.Read()` failures on Go < 1.24:

#### Primary Path: UUIDv4() Vulnerability

1. `UUIDv4()` calls `google/uuid.NewRandom()` which internally uses `crypto/rand.Read()`
2. If `uuid.NewRandom()` fails, `UUIDv4()` falls back to the internal `UUID()` function
3. **No error is returned to the application** - silent security failure occurs

#### Secondary Path: UUID() Vulnerability

1. `UUID()` directly calls `crypto/rand.Read(uuidSeed[:])` to seed its internal state
2. If seeding fails, `UUID()` **silently fails** and returns the zero UUID `"00000000-0000-0000-0000-000000000000"`
3. Applications receive predictable UUIDs with no indication of the security failure

---

### Code Analysis

#### UUIDv4() Vulnerability Path

```go
func UUIDv4() string {
	token, err := uuid.NewRandom()  // Uses crypto/rand.Read() internally
	if err != nil {
		return UUID()  // Dangerous fallback - no error returned to application
	}
	return token.String()
}
```

#### UUID() Vulnerability Path

```go
func UUID() string {
	uuidSetup.Do(func() {
		if _, err := rand.Read(uuidSeed[:]); err != nil {  // Direct crypto/rand.Read() call
			return  // Silent failure - no seeding, uuidCounter remains 0
		}
		uuidCounter = binary.LittleEndian.Uint64(uuidSeed[:8])
	})
	if atomic.LoadUint64(&uuidCounter) <= 0 {
		return "00000000-0000-0000-0000-000000000000"  // Zero UUID returned silently
	}
	// ... generate UUID from counter
}
```

**Root Cause:** Both vulnerabilities stem from `crypto/rand.Read()` failures, occurring through different code paths with the same dangerous silent fallback behavior.

---

## Security Impact

### Severity: CRITICAL

This issue is especially severe because many Fiber middleware packages (session, CSRF, auth, rate-limit, request-ID, etc.) default to `utils.UUIDv4()` for generating security-sensitive identifiers. A failure in `crypto/rand` would cause **every generated identifier across the entire application** to collapse to a single predictable value (the zero UUID), resulting in:

* **Session fixation / universal session hijack**
* **CSRF token predictability and bypass**
* **Authentication token replay**
* **Global identifier collisions leading to severe application breakage**
* **Potential application-wide DoS** due to every request using the same “unique” key, causing cache overwrites, session stomping, corrupted internal maps, and loss of isolation across all users

---

### Attack Scenario

While **entropy exhaustion is extremely rare on modern Linux systems**, *RNG access failures* (e.g., restricted `/dev/random` or `/dev/urandom` access, broken container environments, sandbox restrictions, misconfigured VMs, or FIPS-mode RNG failures) are realistic. In these scenarios on **Go < 1.24**, `crypto/rand` may return errors immediately — triggering the vulnerable fallback paths.

On **Go 1.24+**, `crypto/rand` `Read()` panics on failure, mitigating the silent-zero fallback issue.

---

### Proof of Concept

1. `uuid.NewRandom()` fails (indirect `crypto/rand.Read()` failure)
2. `UUIDv4()` calls `UUID()` as fallback with no error returned
3. `UUID()` seeding fails directly via `crypto/rand.Read(uuidSeed[:])`
4. Zero UUID `"00000000-0000-0000-0000-000000000000"` is returned silently
5. No error is propagated to the application from either function

---

## Affected Versions

* All versions of `github.com/gofiber/utils` containing the `UUIDv4()` or `UUID()` functions
* Applications using Fiber middleware that depend on `UUIDv4()` or `UUID` for security
* **Only applicable to Go < 1.24**; Go 1.24+ panics/block on `crypto/rand` `Read()` failures and is not affected

---

## Mitigation

### Immediate Workaround

Replace usage of `utils.UUIDv4()` with `uuid.New()` or wait for fix:

```go
sessionID := uuid.New()
```

### Recommended Fix

Modify `utils.UUIDv4()` and `utils.UUID()` to fail explicitly when cryptographic randomness is unavailable:

```go
func UUIDv4() string {
	token, err := uuid.NewRandom()
	if err != nil {
		panic(fmt.Sprintf("utils: failed to generate secure UUID: %v", err))
	}
	return token.String()
}

func UUID() string {
    uuidSetup.Do(func() {
        if _, err := rand.Read(uuidSeed[:]); err != nil {
            panic(fmt.Sprintf("utils: failed to seed UUID generator: %v", err))
        }
        uuidCounter = binary.LittleEndian.Uint64(uuidSeed[:8])
    })
    if atomic.LoadUint64(&uuidCounter) <= 0 {
        panic("utils: UUID generator not properly seeded")
    }
    // ... generate UUID from counter
}
```

---

## Detection

Applications can detect if they're affected by:

1. Checking if they use `github.com/gofiber/utils`
2. Searching for `UUIDv4()` and `UUID()` usage in security-critical code paths
3. Reviewing Fiber middleware configurations that rely on defaults of `UUIDv4()` for security identifiers

---

## References

* **Package Repository**: [https://github.com/gofiber/utils](https://github.com/gofiber/utils)
* **Fiber Framework**: [https://github.com/gofiber/fiber](https://github.com/gofiber/fiber)
* **Google UUID Library**: [https://github.com/google/uuid](https://github.com/google/uuid)
* Golang `crypto/rand` behavior changes: [golang/go#66821](https://github.com/golang/go/issues/66821), [Go 1.25.5 source](https://cs.opensource.google/go/go/+/refs/tags/go1.25.5:src/crypto/rand/rand.go;l=80)

---

## Contact

Reported by: [@sixcolors](https://github.com/sixcolors)

---

## Classification

* **OWASP**: A02:2021 - Cryptographic Failures
* **Impact**: Complete compromise of application security model on Go < 1.24
* **Exploitability**: Medium (requires entropy failure)
* **Scope**: All Fiber applications using affected middleware on Go < 1.24

## References
- https://github.com/gofiber/utils/security/advisories/GHSA-m98w-cqp3-qcqr
- https://nvd.nist.gov/vuln/detail/CVE-2025-66565
- https://github.com/gofiber/utils/commit/6c6cf047032b9c8dff43d29f990b4b10e9b02d47
- https://github.com/gofiber/utils
