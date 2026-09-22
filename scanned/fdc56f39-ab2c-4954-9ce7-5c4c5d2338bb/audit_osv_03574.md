# [M] ALPINE-CVE-2026-32249

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-32249
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32249
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=9.1.0011 <9.2.0140-r0

## Details
Vim is an open source, command line text editor. From 9.1.0011 to before 9.2.0137, Vim's NFA regex compiler, when encountering a collection containing a combining character as the endpoint of a character range (e.g. [0-0\u05bb]), incorrectly emits the composing bytes of that character as separate NFA states. This corrupts the NFA postfix stack, resulting in NFA_START_COLL having a NULL out1 pointer. When nfa_max_width() subsequently traverses the compiled NFA to estimate match width for the look-behind assertion, it dereferences state->out1->out without a NULL check, causing a segmentation fault. This vulnerability is fixed in 9.2.0137.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32249
