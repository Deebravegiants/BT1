# [M] CVE-2021-29955

## Summary
Severity: Medium
Advisory: CVE-2021-29955
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-29955
Type: osv

## Details
A transient execution vulnerability, named Floating Point Value Injection (FPVI) allowed an attacker to leak arbitrary memory addresses and may have also enabled JIT type confusion attacks. (A related vulnerability, Speculative Code Store Bypass (SCSB), did not affect Firefox.). This vulnerability affects Firefox ESR < 78.9 and Firefox < 87.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-10/
- https://www.mozilla.org/security/advisories/mfsa2021-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1692972
