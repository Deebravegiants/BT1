# [H] Starlette: SSRF and NTLM credential theft via UNC paths in StaticFiles on Windows

## Summary
Severity: High
Advisory: GHSA-wqp7-x3pw-xc5r
CVE: CVE-2026-48818
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-wqp7-x3pw-xc5r
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <1.1.0

## Details
### Summary

When serving static files on Windows, `StaticFiles` resolves the requested path with [`os.path.realpath`](https://docs.python.org/3/library/os.path.html#os.path.realpath). If a UNC path (such as `\\attacker.com\share`) reaches the resolver, `realpath` causes the process to open a connection to the remote host over SMB (port 445). This is a server-side request forgery (SSRF) that leaks the service account's NTLMv2 credentials to the attacker-controlled host, which can then be cracked offline or relayed to other hosts.

### Details

`StaticFiles.lookup_path()` joins the requested path onto the served directory and calls [`os.path.realpath`](https://docs.python.org/3/library/os.path.html#os.path.realpath) on the result before checking containment with [`os.path.commonpath`](https://docs.python.org/3/library/os.path.html#os.path.commonpath). On Windows, a UNC path is absolute, so [`os.path.join`](https://docs.python.org/3/library/os.path.html#os.path.join) discards the served directory and `realpath` resolves the bare UNC path, triggering the outbound SMB connection and NTLM authentication before the containment check rejects the path. The HTTP response is a benign 404, but the credential disclosure has already happened. POSIX systems are not affected.

This only affects the default configuration (`follow_symlink=False`), which uses [`os.path.realpath`](https://docs.python.org/3/library/os.path.html#os.path.realpath). The `follow_symlink=True` branch uses [`os.path.abspath`](https://docs.python.org/3/library/os.path.html#os.path.abspath), which performs no I/O.

### Impact

Applications running on Windows that serve files with `StaticFiles` (directly, or via a framework built on Starlette such as FastAPI) in the default configuration are affected. `StaticFiles` is typically unauthenticated, so any client can trigger the SMB connection and leak the service account's NTLMv2 hash. A secondary impact is discovering internal hosts reachable over SMB by timing responses for valid versus invalid addresses.

### Mitigation

Applications not running on Windows are not affected. On Windows, serving static files through a dedicated web server (such as nginx or IIS) instead of `StaticFiles` avoids the issue. Blocking outbound SMB (port 445) from the application host prevents the credential disclosure even if a UNC path is resolved.

## References
- https://github.com/Kludex/starlette/security/advisories/GHSA-wqp7-x3pw-xc5r
- https://github.com/Kludex/starlette
