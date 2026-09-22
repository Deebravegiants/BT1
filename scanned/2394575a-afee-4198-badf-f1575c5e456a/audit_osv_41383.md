# [M] Vim: Out-of-bounds Write in SAL Soundfolding

## Summary
Severity: Medium
Advisory: CVE-2026-59857
Aliases: GHSA-m3hf-xcm3-xhm2
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59857
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0725, the single-byte branch of spell_soundfold_sal() in src/spell.c translates a word through a spell file's SAL sound-folding rules into a caller-owned result buffer, but its result writes are guarded with reslen < MAXWLEN, allowing reslen to reach MAXWLEN before res[reslen] = NUL writes one byte past the end of the MAXWLEN-element stack buffer. A boundary-length word passed to soundfold(), or reached via sound-based spell suggestion while a SAL-based spell language is active under a non-multibyte 8-bit encoding, can corrupt the eval_soundfold() stack frame and crash the editor. This issue is fixed in version 9.2.0725.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59857.json
- https://github.com/vim/vim/security/advisories/GHSA-m3hf-xcm3-xhm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-59857
- https://github.com/vim/vim/commit/d22ff1c955ff87e8273210eae125aab0e85b6c30
