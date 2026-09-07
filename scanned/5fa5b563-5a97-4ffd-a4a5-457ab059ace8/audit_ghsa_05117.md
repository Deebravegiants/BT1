# [M] nono-py has proxy-only network fallback bypass on older Linux kernels

## Summary
Severity: Medium
Advisory: GHSA-72w7-mf9g-733p
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-72w7-mf9g-733p
Type: github-advisory

## Affected
- PyPI: `nono-py` — affected >=0.9.0 <0.10.1

## Details
## Summary

On Linux kernels that do not support Landlock network rules, `nono_py.sandboxed_exec()` could run `CapabilitySet.proxy_only(proxy)` without supervising the seccomp-notify proxy-only fallback returned by the Rust core.

In that configuration, a sandboxed child process could remove `HTTP_PROXY` / `HTTPS_PROXY` environment variables or use raw sockets and then open direct TCP connections that should have been denied by proxy-only policy.

The issue affects proxy-only enforcement. It does not mean that all nono-py network blocking is ineffective. ECS validation showed `caps.block_network()` denied regular TCP and ECS metadata TCP on the tested Linux 6.1 host.

## Impact

The intended `proxy_only()` security property is:

- child processes may connect only to the local nono proxy port
- the proxy enforces host allowlists and metadata/link-local denial
- direct TCP to any other target is denied

Before the fix, on kernels without Landlock `AccessNet`, the Python binding applied the sandbox and then executed the child, but did not install and supervise the proxy-only seccomp-notify fallback. A child could therefore bypass the proxy layer in that old-kernel path.

The highest-impact scenario is a sandboxed workload with access to cloud metadata discovery inputs, where direct TCP to a metadata endpoint could retrieve task or instance credentials after proxy environment variables are removed.

## Affected Conditions

The issue requires all of the following:

- Linux runtime.
- Kernel without Landlock network support, such as Linux 6.1. Landlock network rules require Landlock ABI v4 / Linux 6.7 or newer.
- `nono_py.sandboxed_exec()` is used.
- The capability set uses `caps.proxy_only(proxy)`.
- The child process removes or ignores proxy environment variables, or uses raw sockets.

macOS Seatbelt proxy-only enforcement is not affected by this Linux seccomp-notify fallback issue.

## Affected Versions

Known affected builds include nono-py versions that expose and use `CapabilitySet.proxy_only()` through `sandboxed_exec()` before the supervised fallback fix in this working tree.

Earlier versions that did not expose `CapabilitySet.proxy_only()` are not affected by this specific proxy-only enforcement bug, though they may have separate environment-inheritance risks if callers passed broad parent environment variables into sandboxed children.


**CVSS Score Rationale**

| Metric | Value | Rationale |
|---|---|---|
| **Attack Vector (AV)** | L — Local | Exploit is performed by a local process (unsetting env vars or opening raw sockets). Not remotely triggerable. |
| **Attack Complexity (AC)** | H — High | All of the following must be true: Linux runtime; kernel < 6.7 (no Landlock ABI v4); `sandboxed_exec()` used; capability set calls `proxy_only()`; child actively bypasses proxy env vars or uses raw sockets. |
| **Privileges Required (PR)** | L — Low | Attacker is already executing code inside the sandbox — some user-level privilege is required to get there. |
| **User Interaction (UI)** | N — None | No action from a user or operator is needed once the sandboxed child is running. |
| **Scope (S)** | C — Changed | The exploit crosses the sandbox security boundary, allowing the child to reach network resources outside the defined policy scope. |
| **Confidentiality (C)** | H — High | Highest-impact path: direct TCP to cloud metadata endpoint (169.254.169.254) yields IAM / task credentials. |
| **Integrity (I)** | L — Low | Attacker can make arbitrary outbound requests; no direct data modification from the bypass itself, but lateral credential use creates indirect risk. |
| **Availability (A)** | N — None | No denial-of-service impact described or implied. |

---

## References
- https://github.com/always-further/nono-py/security/advisories/GHSA-72w7-mf9g-733p
- https://github.com/nolabs-ai/nono-py/commit/3e67dfa11cbe9514f315fdd36473680c318816d7
- https://github.com/always-further/nono-py
