# [M] Deno: BYONM module resolution allows `package.json` main path traversal to bypass `--allow-read` restrictions

## Summary
Severity: Medium
Advisory: GHSA-968w-xfqw-vp9q
CVE: CVE-2026-49406
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-968w-xfqw-vp9q
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.7.12

## Details
## Summary

When Deno was run in BYONM mode (`nodeModulesDir: "manual"`), the module resolver did not validate that a package's resolved entrypoint stayed within its `node_modules/<pkg>/` directory. A malicious `package.json` whose `main` field contained `..` segments was able to resolve to an arbitrary path on disk, and the resolver then read that file without consulting the `--allow-read` allowlist. This let a `require("evil-pkg")` call return the contents of a file that a direct `Deno.readTextFileSync(...)` call would have been blocked from reading.

## Details

In BYONM mode, Deno resolved npm packages directly from a user-managed `node_modules` tree. Resolution of `require("pkg")` proceeded by reading `pkg/package.json`, taking the `main` field, joining it to the package directory, and loading the result as a module.

The path joined from `main` was not constrained to the package root. A `package.json` such as:

```json
{ "main": "../../../secret.json" }
```

resolved to `node_modules/pkg/../../../secret.json`, escaping `node_modules` entirely. The BYONM permission check accepted any path that contained a `node_modules` component and did not reject `..` traversal, so the resolved path was loaded without a read-permission check.

Because resolution loaded JSON entrypoints by parsing their contents and returning them through `require`, this exposed the contents of arbitrary `.json` files reachable by the OS user to the requiring code, even when `--allow-read` had been narrowed to a specific directory.

The same file accessed via `Deno.readTextFileSync` was correctly blocked. The bug was that module resolution did not enforce the same read-permission boundary that the filesystem APIs enforced.

## Proof of concept

The reporter supplied a self-contained PoC. Layout:

```
/tmp/deno_byonm_poc/
├── app/
│   ├── deno.json            (BYONM enabled)
│   ├── exploit.ts           (require("evil-pkg"))
│   └── node_modules/
│       └── evil-pkg/
│           └── package.json (main: "../../../secret.json")
└── secret.json              (outside --allow-read scope)
```

Run:

```bash
deno run --no-prompt --allow-read=/tmp/deno_byonm_poc/app exploit.ts
```

Observed:

- `Deno.readTextFileSync("/tmp/deno_byonm_poc/secret.json")` — blocked, as
  expected.
- `require("evil-pkg")` — returned the parsed contents of `secret.json`,
  bypassing the read allowlist.

A control run with BYONM disabled (`--no-config`) blocked the `require` call.

## Impact

The vulnerability allowed a hostile npm package installed under a BYONM `node_modules` to read JSON files outside the directories granted via `--allow-read`, up to the privileges of the OS user running Deno. In practice this exposed configuration and credential files (`.env.json`, cloud credentials, package lockfiles, etc.) that the user had deliberately excluded from the read scope.

The vulnerability did not grant any capability beyond what the OS user already held, did not affect runs that granted unrestricted `--allow-read`, and required the user to have installed and then required a hostile package, i.e. an existing supply-chain compromise. The reason it warranted a security advisory rather than a routine bug fix is that Deno's permission model
promised that `--allow-read=<scope>` was a hard boundary *even over untrusted npm code*, and that promise was broken.

Not affected:

- Runs without BYONM (default npm resolution went through a separate code
  path that rejected the traversal).
- Runs with full `--allow-read` (no boundary to bypass).
- Non-JSON entrypoints, in practice — `.js`/`.cjs`/`.mjs` targets executed
  rather than exposing file contents, which already implied attacker code
  execution within the granted permission set.

## Workarounds

Users on unpatched versions could mitigate by:

- Avoiding BYONM mode (`nodeModulesDir: "manual"`) for projects that depended
  on untrusted packages.
- Auditing `package.json` `main` fields in `node_modules` for `..` segments
  before running.
- Granting `--allow-read` only when the read scope already covered every file
  the OS user could see (in which case there was no boundary to bypass and no
  additional exposure).

## References
- https://github.com/denoland/deno/security/advisories/GHSA-968w-xfqw-vp9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-49406
- https://github.com/denoland/deno
