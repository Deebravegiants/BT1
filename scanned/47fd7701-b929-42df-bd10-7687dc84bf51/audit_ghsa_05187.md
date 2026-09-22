# [H] Deno: Permission Bypass via Unicode Normalization Mismatch on macOS (APFS)

## Summary
Severity: High
Advisory: GHSA-8xpq-cjcf-3wh9
CVE: CVE-2026-49401
CWE: CWE-176, CWE-41
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-8xpq-cjcf-3wh9
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <2.7.14

## Details
## Summary

Deno's permission system enforces filesystem and execution restrictions by
comparing the requested path against the path supplied to `--deny-read`,
`--deny-write`, `--deny-run`, or `--deny-ffi`. On macOS, that comparison was
done at the raw-byte level while the APFS filesystem treats different Unicode
spellings of the same name as the same file.

That means a program could reach a denied path by spelling it differently than
the deny rule. For example, with `--deny-read=/secrets/passwörter.txt`, a
script could still read the file by opening `/secrets/passwo\u0308rter.txt`
(NFD instead of NFC), or `/SECRETS/PASSWÖRTER.txt` (different case, since
default APFS volumes are case-insensitive). Other forms include ligature
characters (`ﬁ` vs `fi`, `ﬀ` vs `ff`, …) and German `ß` vs `ss`.

The denied path and the requested path differed at the byte level, so Deno's
permission check passed; the kernel then resolved them to the same inode and
served the file anyway. The same flaw affected `--deny-write`, `--deny-run`,
and `--deny-ffi`, which share the same path-comparison code.

## Am I affected?

You are potentially affected if **all** of the following are true:

1. You run Deno on **macOS** (the issue is specific to APFS path-equivalence
   rules; Linux and Windows are not affected by this variant).
2. You rely on `--deny-read`, `--deny-write`, `--deny-run`, or `--deny-ffi`
   as a security boundary against less-trusted code — a dependency, plugin,
   or attacker-controlled input.
3. The protected path contains characters that have alternate Unicode
   spellings — most commonly accented characters (`é`, `ñ`, `ö`, …), German
   `ß`, or Latin ligatures — or you rely on case-sensitivity on a default
   APFS volume.

If you only run fully trusted code, or your deny rules cover paths that are
pure ASCII with no case-sensitive aliases, you are not exposed to this
specific bypass.

## Impact

A program running with broad `--allow-read` (or `--allow-write` /
`--allow-run` / `--allow-ffi`) but with `--deny-*` carve-outs for specific
paths could read, write, execute, or load via FFI those denied paths by
referring to them through a Unicode- or case-equivalent spelling. The sandbox
model on macOS was weaker than the flags suggested.

## Workaround

If you cannot upgrade immediately:

- Prefer `--allow-*` allowlists over `--deny-*` denylists. Allow rules match
   against the original specifier, so an attacker-supplied alternate spelling
   will not match a path you didn't explicitly grant.
- Do not rely on case-sensitivity of paths on macOS for security boundaries;
   default APFS volumes are case-insensitive.

## Fix

On macOS, Deno now normalizes both the deny-rule path and the requested path
to NFC and applies Unicode case folding before comparing them. This matches
how APFS resolves paths at the inode level, so byte-different but equivalent
spellings are now rejected by the same deny rule.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-8xpq-cjcf-3wh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-49401
- https://github.com/denoland/deno
