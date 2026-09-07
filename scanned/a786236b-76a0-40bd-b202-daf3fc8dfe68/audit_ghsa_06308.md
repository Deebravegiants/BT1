# [C] gRPC Erlang package vulnerable to Remote Code Execution with attacker-controlled gRPC payloads

## Summary
Severity: Critical
Advisory: GHSA-grp7-v8xh-rj7h
CVE: CVE-2026-48853
CWE: CWE-502, CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-grp7-v8xh-rj7h
Type: github-advisory

## Affected
- Hex: `grpc` — affected >=0.4.0 <1.0.0

## Details
### Summary

`GRPC.Codec.Erlpack.decode/2` calls `:erlang.binary_to_term/1` directly on the raw gRPC message body without the `:safe` option. Any unauthenticated peer that can reach a gRPC endpoint with `Content-Type: application/grpc+erlpack` can crash the entire BEAM node via atom table exhaustion or, if a decoded fun term flows into a call site that invokes it, achieve remote code execution inside the server process.

### Details

**Root cause** — `lib/grpc/codec/erlpack.ex` implements `decode/2` as a bare `:erlang.binary_to_term(binary)` call with no `:safe` flag, no size limit, and no type validation. This has two independent exploitation paths:

**1. DoS via atom exhaustion** — BEAM atoms are never garbage-collected and the global atom table is bounded (~1,048,576 entries). A crafted payload encoding large numbers of fresh atoms saturates the table and crashes the entire VM, taking down all applications on the node.

**2. RCE via fun materialization** — Without `:safe`, `binary_to_term/1` reconstructs fun and external-fun terms from wire data. If the decoded value reaches any call site that applies it (e.g. `Enum.map`, `Task.async`, direct invocation), attacker-controlled code executes inside the server process.

**Configuration requirement:** `GRPC.Codec.Erlpack` is not registered by default and must be explicitly added to the server's `codecs` option.

### PoC

1. Start a gRPC server with `codecs: [GRPC.Codec.Erlpack]`.
2. Open an HTTP/2 connection to the server.
3. Send a gRPC-framed POST to any RPC path with `Content-Type: application/grpc+erlpack` and a body of `:erlang.term_to_binary(fn -> <malicious_code> end)`.
4. The server's `decode/2` materializes the fun; any downstream call site that invokes the decoded value executes the attacker's code.
5. For DoS only: send payloads encoding fresh atoms in a loop until the atom table is exhausted and the VM crashes.

### Impact

Affects `grpc` ≥ 0.4.0. Any server that explicitly registers `GRPC.Codec.Erlpack` is vulnerable to unauthenticated node-level DoS and potentially RCE.

### References

* Introduction commit: https://github.com/elixir-grpc/grpc/commit/25bcc569fe2cc4478531a6c546c923205fc751c9
* Patch commit: https://github.com/elixir-grpc/grpc/commit/272a97a5ea1b46af1819f14a831fcf35fc91f992

## References
- https://github.com/elixir-grpc/grpc/security/advisories/GHSA-grp7-v8xh-rj7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-48853
- https://github.com/elixir-grpc/grpc/pull/540
- https://github.com/elixir-grpc/grpc/commit/272a97a5ea1b46af1819f14a831fcf35fc91f992
- https://cna.erlef.org/cves/CVE-2026-48853.html
- https://github.com/elixir-grpc/grpc
- https://github.com/elixir-grpc/grpc/releases/tag/v1.0.0
- https://osv.dev/vulnerability/EEF-CVE-2026-48853
