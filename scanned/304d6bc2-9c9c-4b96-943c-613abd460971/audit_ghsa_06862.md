# [H] gRPC-Go: xDS RBAC and HTTP/2 Vulnerabilities

## Summary
Severity: High
Advisory: GHSA-hrxh-6v49-42gf
CWE: CWE-248, CWE-770, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-hrxh-6v49-42gf
Type: github-advisory

## Affected
- Go: `google.golang.org/grpc` — affected >=0 <1.82.1

## Details
Multiple security vulnerabilities have been identified and addressed in grpc-go affecting the xDS RBAC authorization engine (internal/xds/rbac) and the HTTP/2 transport server implementation (internal/transport). These vulnerabilities could result in:

- Authorization Bypass (Fail-Open) when translating xDS RBAC policies containing `Metadata` or `RequestedServerName` fields.
- Denial of Service (High CPU Consumption) due to an HTTP/2 Rapid Reset mitigation bypass during client-initiated stream resets.
- Denial of Service (Server Panic) when parsing crafted xDS RBAC policies containing `NOT` rules around unsupported fields.


### Impact
_What kind of vulnerability is it? Who is impacted?_

#### xDS RBAC Authorization Bypass via `Metadata` & `RequestedServerName` matchers

- Affected Component: xDS RBAC 
- Impact: When building policy matchers for gRPC RBAC from xDS configurations, unsupported `permission` and `principal` rules (specifically `Metadata` and `RequestedServerName`) were silently ignored and treated as no-ops.
  - If an authorization policy relied purely on these matchers for access control, treating those rules as no-ops effectively removed the restrictions.
- If these unsupported rules were nested inside logical `NOT` rules (`Permission_NotRule` / `Principal_NotId`) or multi-condition `OR/AND` rules, silently dropping them changed the boolean logic flow of the authorization engine.

As a result, policy evaluation decisions could fail open, allowing unauthorized clients to access protected gRPC services or resources.

#### HTTP/2 Rapid Reset Mitigation Bypass / Denial of Service via Stream Aborts

- Affected Component: HTTP/2 transport
- Impact: Earlier mitigations in grpc-go for HTTP/2 Rapid Reset only applied threshold checks to items that directly resulted in control frames being written back to the wire, such as `SETTINGS` ACKs or server-initiated `RST_STREAM`s.

When a client initiated a rapid flood of stream creation (`HEADERS`) immediately followed by stream termination `RST_STREAM`, items queued up in the control buffer without counting against the transport response frame threshold. An attacker can repeatedly trigger this flood sequence to bypass reader blocking, resulting in high CPU usage, and Denial of Service (DoS).

#### Denial of Service (Panic) in xDS RBAC Engine via Unsupported Fields inside NOT Rules

- Affected Component: xDS RBAC 
- Impact: The xDS RBAC policy translators recursively generate matchers for nested rules. When a `NOT` rule wrapped an unsupported or unhandled field (such as `SourcedMetadata`), the recursive step returned an empty matcher. This could result in a runtime panic when the RBAC engine attempts to authorize an incoming request.

An attacker or misconfigured/malicious xDS management server delivering an LDS/RDS update containing a `NOT` rule around an unhandled field causes the gRPC server process to crash immediately (CWE-248 / Denial of Service).

### Patches
_Has the problem been patched? What versions should users upgrade to?_

All three issues have been fixed in `master` and will be released in 1.82.1 shortly.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

If upgrading grpc-go immediately is not possible, apply the following workarounds based on your deployment architecture:

* For xDS RBAC Vulnerabilities & Panics: Ensure that upstream xDS management servers do not push RBAC policies containing `Metadata`, `RequestedServerName`, or `NOT` rules wrapping unsupported fields (such as `SourcedMetadata`) to grpc-go servers.
* For HTTP/2 Rapid Reset DOS: Configure upstream reverse proxies or load balancers (such as Envoy) with strict HTTP/2 `max_concurrent_streams` limits and active rate limiting on `RST_STREAM` frequency per connection.

### Severity

  | Vulnerability | Qualitative Severity | Approximate CVSS v3.1 Score | Primary Impact |
  | :--- | :--- | :--- | :--- |
  | **xDS RBAC Authorization Bypass** | **High** | `8.2` | Unauthorized Access / Fail-Open |
  | **HTTP/2 Rapid Reset DOS Bypass** | **High** | `7.5` | High CPU Consumption / Denial of Service |
  | **xDS RBAC Engine Server Panic** | **Medium** | `5.9` | Process Crash / Denial of Service |

## References
- https://github.com/grpc/grpc-go/security/advisories/GHSA-hrxh-6v49-42gf
- https://github.com/grpc/grpc-go/pull/9236
- https://github.com/grpc/grpc-go/commit/4ea465d4ab98013f72a142fe0fc89c19770b2935
- https://github.com/grpc/grpc-go
- https://github.com/grpc/grpc-go/releases/tag/v1.82.1
