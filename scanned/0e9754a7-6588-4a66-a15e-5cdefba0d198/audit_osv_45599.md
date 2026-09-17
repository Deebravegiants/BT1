# [C] Wasmtime doesn't fully sandbox all the Windows device filenames

## Summary
Severity: Critical
Advisory: JLSEC-2026-1348
Ecosystem: Julia
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/JLSEC-2026-1348
Type: osv

## Affected
- Julia: `Wasmtime_jll` — affected >=0 <24.0.2+0

## Details
### Impact

Wasmtime's filesystem sandbox implementation on Windows blocks access to special device filenames such as "COM1", "COM2", "LPT0", "LPT1", and so on, however it did not block access to the special device filenames which use superscript digits, such as "COM¹", "COM²", "LPT⁰", "LPT¹", and so on. Untrusted Wasm programs that are given access to any filesystem directory could bypass the sandbox and access devices through those special device filenames with superscript digits, and through them gain access peripheral devices connected to the computer, or network resources mapped to those devices. This can include modems, printers, network printers, and any other device connected to a serial or parallel port, including emulated USB serial ports.

### Patches

Patch releases for Wasmtime have been issued as 24.0.2, 25.0.3, and 26.0.1. Users of Wasmtime 23.0.x and prior are recommended to upgrade to one of these patched versions.

### Workarounds

There are no known workarounds for this issue. Affected Windows users are recommended to upgrade.

### References

  - [Microsoft's documentation](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions) of the special device filenames
  - [ISO-8859-1](https://en.wikipedia.org/wiki/ISO/IEC_8859-1)
  - [The original PR reporting the issue](https://github.com/bytecodealliance/cap-std/pull/371)

## References
- https://en.wikipedia.org/wiki/ISO/IEC_8859-1
- https://github.com/advisories/GHSA-c2f5-jxjv-2hh8
- https://github.com/bytecodealliance/cap-std/pull/371
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-c2f5-jxjv-2hh8
- https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
- https://nvd.nist.gov/vuln/detail/CVE-2024-51745
- https://rustsec.org/advisories/RUSTSEC-2024-0438.html
