# [M] GNU Bison allows for an execution of an arbitrary program during HTML report generation due to...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1345
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:L/SC:L/SI:L/SA:L/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/JLSEC-2026-1345
Type: osv

## Affected
- Julia: `Bison_jll` — affected unspecified

## Details
GNU Bison allows for an execution of an arbitrary program during HTML report generation due to improper handling of grammar-defined configuration variables. A grammar file can override the executable used for the XML‑to‑HTML transformation step via %define tool.xsltproc, which is accepted without restriction and passed directly to execvp().

When running bison --html on a attacker-provided grammar, this behavior allows execution of an arbitrary program with the privileges of the Bison process.

Maintainers of this project were notified about this vulnerability, and fixed the issue in commit 3169c1e7a2c6acc4c59dfcf8b089896d6881925b. However, they did not provide vulnerable version range. Version 3.8.2 was tested and confirmed as vulnerable, other versions were not tested but might also be vulnerable.

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-56389
- https://cgit.git.savannah.gnu.org/cgit/bison.git
- https://cgit.git.savannah.gnu.org/cgit/bison.git/
- https://cgit.git.savannah.gnu.org/cgit/bison.git/commit/?id=3169c1e7a2c6acc4c59dfcf8b089896d6881925b
- https://github.com/advisories/GHSA-735p-4prj-f62v
- https://nvd.nist.gov/vuln/detail/CVE-2026-56389
