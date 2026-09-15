# [M] GNU Wget through 1.25.0, fixed in commit 37a40fc, contains a heap buffer underread vulnerability...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1158
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1158
Type: osv

## Affected
- Julia: `wget_jll` — affected unspecified

## Details
GNU Wget through 1.25.0, fixed in commit 37a40fc, contains a heap buffer underread vulnerability in the `clean_metalink_string()` function within `src/metalink.c` that allows a malicious server to trigger memory corruption by serving a Metalink document containing a whitespace-only URL. Attackers can cause the function to decrement a pointer past the start of the buffer when processing an all-whitespace Metalink URL, potentially leading to abnormal program behavior.

## References
- https://github.com/advisories/GHSA-fxf9-rxpj-26gx
- https://gitlab.com/gnuwget/wget/-/commit/37a40fcb450153f69537c7cbc2a7a4fb0b6f7826
- https://nvd.nist.gov/vuln/detail/CVE-2026-58469
- https://www.vulncheck.com/advisories/gnu-wget-heap-buffer-underread-via-metalink-url-parsing
