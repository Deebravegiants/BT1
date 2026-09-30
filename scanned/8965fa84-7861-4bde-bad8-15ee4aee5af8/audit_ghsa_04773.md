# [M] Deno: WebSocket API sandbox bypass via missing post-DNS check

## Summary
Severity: Medium
Advisory: GHSA-83pc-3rw9-qpwj
CVE: CVE-2026-49860
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-83pc-3rw9-qpwj
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.8.1

## Details
## Summary

When a WebSocket connection was opened, Deno checked the destination hostname
against `--deny-net` rules but did not re-check the IP addresses that hostname
resolved to. An attacker-controlled script could use a specially crafted domain
name that passes the hostname check yet resolves to a denied IP, bypassing the
network restriction entirely.

## Impact

Code running under `--deny-net` could connect to hosts that the user intended
to block. In practice this means network isolation rules — for example,
blocking access to `localhost` or internal services — could be silently
circumvented by a malicious or compromised dependency.

`Deno.connect` and `fetch()` were not affected by this specific issue (a
companion advisory covers `fetch()`).

## Who is affected

Users who:

- run untrusted or third-party code with `deno run`, and
- rely on `--deny-net` to restrict which hosts that code can reach.

If you do not use `--deny-net`, or if you only run fully trusted code, you are
not affected.

## Workaround

No workaround is available short of upgrading. If upgrading immediately is not
possible, avoid granting `--allow-net` to untrusted code that also has
`--deny-net` restrictions you depend on for security.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-83pc-3rw9-qpwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-49860
- https://github.com/denoland/deno
