# [C] Fiber has an insecure fallback in utils.UUIDv4() / utils.UUID() — predictable / zero‑UUID on crypto/rand failure

## Summary
Severity: Critical
Advisory: GHSA-68rr-p4fp-j59v
CVE: CVE-2025-66630
CWE: CWE-338
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-68rr-p4fp-j59v
Type: github-advisory

## Affected
- Go: `github.com/gofiber/fiber/v2` — affected >=0 <2.52.11

## Details
Fiber v2 contains an internal vendored copy of `gofiber/utils`, and its functions `UUIDv4()` and `UUID()` inherit the same critical weakness described in the upstream advisory. On **Go versions prior to 1.24**, the underlying `crypto/rand` implementation **can return an error** if secure randomness cannot be obtained. In such cases, these Fiber v2 UUID functions silently fall back to generating predictable values — the all-zero UUID `00000000-0000-0000-0000-000000000000`.

On Go **1.24+**, the language guarantees that `crypto/rand` no longer returns an error (it will block or panic instead), so this vulnerability primarily affects **Fiber v2 users running Go 1.23 or earlier**, which Fiber v2 officially supports.

Because no error is returned by the Fiber v2 UUID functions, application code may unknowingly rely on *predictable, repeated, or low-entropy identifiers* in security-critical pathways. This is especially impactful because many Fiber v2 middleware components (session middleware, CSRF, rate limiting, request-ID generation, etc.) **default to using `utils.UUIDv4()`**.

Impact includes, but is not limited to:

* **Session fixation or hijacking** (predictable session IDs)
* **CSRF token forgery** or bypass
* **Authentication replay / token prediction**
* **Potential denial-of-service (DoS):** if the zero UUID is generated, key-based structures (sessions, rate-limits, caches, CSRF stores) may collapse into a single shared key, causing overwrites, lock contention, or state corruption
* **Request-ID collisions**, undermining logging and trace integrity
* **General compromise** of confidentiality, integrity, and authorization logic relying on UUIDs for uniqueness or secrecy

All Fiber v2 versions containing the internal `utils.UUIDv4()` / `utils.UUID()` implementation are affected when running on **Go <1.24**. **No patched Fiber v2 release currently exists.**

---

## Suggested Mitigations / Workarounds

Update to the latest version of Fiber v2.

---

### Likelihood / Environmental Factors

It’s important to note that **entropy exhaustion on modern Linux systems is extremely rare**, as the kernel’s CSPRNG is resilient and non-blocking. However, **entropy-source failures** — where `crypto/rand` cannot read from its underlying provider — are significantly more likely in certain environments.

This includes containerized deployments, restricted sandboxes, misconfigured systems lacking read access to `/dev/urandom` or platform-equivalent sources, chrooted or jailed environments, embedded devices, or systems with non-standard or degraded randomness providers. On **Go <1.24**, such failures cause `crypto/rand` to return an error, which the Fiber v2 UUID functions currently treat as a signal to silently generate predictable UUIDs, including the zero UUID. This silent fallback is the root cause of the vulnerability.

---

## References

* Upstream advisory for `gofiber/utils`: **GHSA-m98w-cqp3-qcqr**
* Source repositories:

  * `github.com/gofiber/fiber`
  * `github.com/gofiber/utils`

---

## Credits / Reporter

Reported by **@sixcolors** (Fiber Maintainer / Security Team)

## References
- https://github.com/gofiber/fiber/security/advisories/GHSA-68rr-p4fp-j59v
- https://nvd.nist.gov/vuln/detail/CVE-2025-66630
- https://github.com/gofiber/fiber/commit/eb874b6f6c5896b968d9b0ab2b56ac7052cb0ee1
- https://github.com/gofiber/fiber
- https://github.com/gofiber/fiber/releases/tag/v2.52.11
