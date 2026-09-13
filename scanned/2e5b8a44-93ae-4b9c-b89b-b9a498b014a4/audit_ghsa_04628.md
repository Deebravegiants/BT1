# [M] Deno: `fetch()` API sandbox bypass via missing DNS resolution check

## Summary
Severity: Medium
Advisory: GHSA-cpgj-f7g3-2pp2
CVE: CVE-2026-49859
CWE: CWE-693, CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-cpgj-f7g3-2pp2
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.8.1

## Details
## Summary

When `fetch()` was called, Deno checked the destination hostname against
`--deny-net` rules but did not re-check the IP addresses that hostname
resolved to. An attacker-controlled script could use a specially crafted domain
name that passes the hostname check yet resolves to a denied IP, bypassing the
network restriction entirely.

## Impact

Code running under `--deny-net` could reach hosts that the user intended to
block. In practice this means network isolation rules — for example, blocking
access to `localhost` or internal services — could be silently circumvented by
a malicious or compromised dependency.

A companion advisory covers the same class of issue in the WebSocket API.

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

## Fix

The `fetch()` DNS resolver now performs a post-resolution check on every IP
address before passing it to the HTTP connector, consistent with how
`Deno.connect` already behaved.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-cpgj-f7g3-2pp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-49859
- https://github.com/denoland/deno
