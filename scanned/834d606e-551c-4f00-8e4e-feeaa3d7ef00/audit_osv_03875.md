# [M] ALPINE-CVE-2026-59857

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-59857
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-59857
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0725, the single-byte branch of spell_soundfold_sal() in src/spell.c translates a word through a spell file's SAL sound-folding rules into a caller-owned result buffer, but its result writes are guarded with reslen < MAXWLEN, allowing reslen to reach MAXWLEN before res[reslen] = NUL writes one byte past the end of the MAXWLEN-element stack buffer. A boundary-length word passed to soundfold(), or reached via sound-based spell suggestion while a SAL-based spell language is active under a non-multibyte 8-bit encoding, can corrupt the eval_soundfold() stack frame and crash the editor. This issue is fixed in version 9.2.0725.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-59857
