# [H] Authlib: JWS/JWT accepts unknown crit headers (RFC violation → possible authz bypass)

## Summary
Severity: High
Advisory: GHSA-9ggr-2464-2j32
CVE: CVE-2025-59420
CWE: CWE-345, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-9ggr-2464-2j32
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.4

## Details
## Summary
Authlib’s JWS verification accepts tokens that declare unknown critical header parameters (`crit`), violating RFC 7515 “must‑understand” semantics. An attacker can craft a signed token with a critical header (for example, `bork` or `cnf`) that strict verifiers reject but Authlib accepts. In mixed‑language fleets, this enables split‑brain verification and can lead to policy bypass, replay, or privilege escalation.

## Affected Component and Versions
- Library: Authlib (JWS verification)
- API: `authlib.jose.JsonWebSignature.deserialize_compact(...)`
- Version tested: 1.6.3
- Configuration: Default; no allowlist or special handling for `crit`

## Details
RFC 7515 (JWS) §4.1.11 defines `crit` as a “must‑understand” list: recipients MUST understand and enforce every header parameter listed in `crit`, otherwise they MUST reject the token. Security‑sensitive semantics such as token binding (e.g., `cnf` from RFC 7800) are often conveyed via `crit`.

Observed behavior with Authlib 1.6.3:
- When a compact JWS contains a protected header with `crit: ["cnf"]` and a `cnf` object, or `crit: ["bork"]` with an unknown parameter, Authlib verifies the signature and returns the payload without rejecting the token or enforcing semantics of the critical parameter.
- By contrast, Java Nimbus JOSE+JWT (9.37.x) and Node `jose` v5 both reject such tokens by default when `crit` lists unknown names.

Impact in heterogeneous fleets:
- A strict ingress/gateway (Nimbus/Node) rejects a token, but a lenient Python microservice (Authlib) accepts the same token. This split‑brain acceptance bypasses intended security policies and can enable replay or privilege escalation if `crit` carries binding or policy information.

## Proof of Concept (PoC)
This repository provides a multi‑runtime PoC demonstrating the issue across Python (Authlib), Node (`jose` v5), and Java (Nimbus).

### Prerequisites
- Python 3.8+
- Node.js 18+
- Java 11+ with Maven

### Setup

Enter the directory **authlib-crit-bypass-poc** & run following commands.
```bash
make setup
make tokens
```

### Tokens minted
- `tokens/unknown_crit.jwt` with protected header:
  `{ "alg": "HS256", "crit": ["bork"], "bork": "x" }`
- `tokens/cnf_header.jwt` with protected header:
  `{ "alg": "HS256", "crit": ["cnf"], "cnf": {"jkt": "thumb-42"} }`

### Reproduction
Run the cross‑runtime demo:
```bash
make  demo
```

Expected output for each token (strict verifiers reject; Authlib accepts):

For `tokens/unknown_crit.jwt`:
```
Strict(Nimbus): REJECTED (unknown critical header: bork)
Strict(Node jose): REJECTED (unrecognized crit)
Lenient(Authlib): ACCEPTED -> payload={'sub': '123', 'role': 'user'}
```

For `tokens/cnf_header.jwt`:
```
Strict(Nimbus): REJECTED (unknown critical header: cnf)
Strict(Node jose): REJECTED (unrecognized crit)
Lenient(Authlib): ACCEPTED -> payload={'sub': '123', 'role': 'user'}
```

Environment notes:
- Authlib version used: `1.6.3` (from PyPI)
- Node `jose` version: `^5`
- Nimbus JOSE+JWT version: `9.37.x`
- HS256 secret is 32 bytes to satisfy strict verifiers: `0123456789abcdef0123456789abcdef`

## Impact
- Class: Violation of JWS `crit` “must‑understand” semantics; specification non‑compliance leading to authentication/authorization policy bypass.
- Who is impacted: Any service that relies on `crit` to carry mandatory security semantics (e.g., token binding via `cnf`) or operates in a heterogeneous fleet with strict verifiers elsewhere.
- Consequences: Split‑brain acceptance (gateway rejects while a backend accepts), replay, or privilege escalation if critical semantics are ignored.

## References
- RFC 7515: JSON Web Signature (JWS), §4.1.11 `crit`
- RFC 7800: Proof‑of‑Possession Key Semantics for JWTs (`cnf`)

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-9ggr-2464-2j32
- https://nvd.nist.gov/vuln/detail/CVE-2025-59420
- https://github.com/authlib/authlib/commit/6b1813e4392eb7c168c276099ff7783b176479df
- https://github.com/authlib/authlib
- https://lists.debian.org/debian-lts-announce/2025/10/msg00032.html
