# [H] Externally Controlled Format String in Scripting Functions

## Summary
Severity: High
Advisory: GHSA-q3gg-m8hr-h4x4
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-q3gg-m8hr-h4x4
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.1.1

## Details
The `rquickjs` crate used by SurrealDB implements Rust bindings to the QuickJS C library and is used to execute SurrealDB scripting functions. The `rquickjs` function `Exception::throw_type` takes a string and returns an error object. Prior to version `0.4.2` of the crate, this string would be fed directly into `printf`, which will receive the error string as a format string with no additional arguments, leading to undefined behavior. This issue triggers when a SurrealDB scripting function returns an error and its input contains a format string such as `%s` or `%d`. 

This vulnerability can only affect SurrealDB servers explicitly enabling the scripting capability with `--allow-scripting` or `--allow-all` and equivalent environment variables `SURREAL_CAPS_ALLOW_SCRIPT=true` and `SURREAL_CAPS_ALLOW_ALL=true`.

### Impact

An attacker with privileges to execute scripting functions with arbitrary inputs may be able to exploit this format string vulnerability in order read arbitrary memory from the remote SurrealDB process. A format string vulnerability may also be further exploited to execute arbitrary code with the privileges of the SurrealDB process.

The fact that error messages are limited to 256 bytes coupled with [exploit mitigation features supported in Rust executables](https://doc.rust-lang.org/rustc/exploit-mitigations.html#exploit-mitigations-1) may somewhat increase the complexity of exploiting this vulnerability to reliably achieve remote code execution in practice.

### Patches

- Version 1.1.1 and later are not affected by this issue.

### Workarounds

Users unable to update should restrict access from untrusted users to define and execute scripting functions. This can be achieved by removing the scripting capability by default or with `--deny-scripting` and equivalent environment variable `SURREAL_CAPS_DENY_SCRIPT=true`. If not possible, network access should be limited to trusted users.

### References

- https://github.com/surrealdb/surrealdb/issues/3327
- https://github.com/surrealdb/surrealdb/pull/3332
- https://github.com/DelSkayn/rquickjs/pull/247

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-q3gg-m8hr-h4x4
- https://github.com/surrealdb/surrealdb/issues/3327
- https://github.com/surrealdb/surrealdb/pull/3332
- https://github.com/surrealdb/surrealdb
