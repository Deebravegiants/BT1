# [M] mcp-kubernetes-server has a Command Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-hjm5-xgj8-vwj6
CVE: CVE-2025-59376
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-hjm5-xgj8-vwj6
Type: github-advisory

## Affected
- PyPI: `mcp-kubernetes-server` — affected >=0

## Details
`mcp-kubernetes-server` does not correctly enforce the `--disable-write` / `--disable-delete` protections when commands are chained. The server only inspects the first token to decide whether an operation is write/delete, which allows a read-like command to be followed by a write action using shell metacharacters (e.g., `kubectl version; kubectl delete pod <name>`). A remote attacker who can invoke the server may therefore bypass the intended write/delete restrictions and perform state-changing operations against the Kubernetes cluster.

**Affected versions:** through `0.1.11` (no patched release available as of now).

**Mitigations:**
- Run with `--disable-kubectl` and/or `--disable-helm` to fully block those execution paths.
- Put the server behind an allow-list proxy restricting allowed subcommands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59376
- https://github.com/feiskyer/mcp-kubernetes-server
- https://github.com/feiskyer/mcp-kubernetes-server/blob/78957b6c1a3982080cf6fcaac6f6e9014116a71c/src/mcp_kubernetes_server/main.py#L106-L137
- https://github.com/william31212/CVE-Requests-1896609
