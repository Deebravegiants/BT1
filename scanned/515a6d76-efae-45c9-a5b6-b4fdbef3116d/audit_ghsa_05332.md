# [M] Deno: process.loadEnvFile() bypasses env permission checks and mutates process.env with only read access

## Summary
Severity: Medium
Advisory: GHSA-4c8g-jvcx-v4hv
CVE: CVE-2026-49983
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-4c8g-jvcx-v4hv
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.8.1

## Details
## Summary

In Deno, environment access is gated by the `env` permission. You can deny it
with `--deny-env`, or restrict it to a specific allowlist with
`--allow-env=FOO,BAR`. The expectation is that a program running without `env`
permission cannot change `process.env`.

`process.loadEnvFile()` (the Node-compatible API for loading variables from a
`.env` file) does **not** honor this. It only checks that the program has
**read** permission for the dotenv file, then writes every key in that file
into the process environment — even when `env` access is denied.

In effect, **`--allow-read` plus a writable or attacker-controlled `.env` file
is enough to defeat `--deny-env`.**

## Am I affected?

You are potentially affected if **all** of the following are true:

1. You run Deno **v2.3.0 or newer**.
2. Your program (or any dependency it imports) calls `process.loadEnvFile()`
   from `node:process`.
3. You rely on Deno's permission model — specifically `--deny-env`, an
   `--allow-env=…` allowlist, or running without granting `env` — as a
   security boundary.
4. The `.env` path passed to `loadEnvFile()` can be controlled or modified by
   a less-trusted party (untrusted input, user-writable directory, third-party
   dependency, etc.) and is covered by your `--allow-read` grant.

If your program does not use `process.loadEnvFile()` at all, or if it already
grants full `env` access, this advisory does not change your risk.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-4c8g-jvcx-v4hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-49983
- https://github.com/denoland/deno
