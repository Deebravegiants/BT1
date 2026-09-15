# [H] CVE-2025-1933

## Summary
Severity: High
Advisory: CVE-2025-1933
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-1933
Type: osv

## Details
On 64-bit CPUs, when the JIT compiles WASM i32 return values they can pick up bits from left over memory. This can potentially cause them to be treated as a different type. This vulnerability affects Firefox < 136, Firefox ESR < 115.21, Firefox ESR < 128.8, Thunderbird < 136, and Thunderbird < 128.8.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00006.html
- https://www.mozilla.org/security/advisories/mfsa2025-15/
- https://www.mozilla.org/security/advisories/mfsa2025-16/
- https://www.mozilla.org/security/advisories/mfsa2025-17/
- https://www.mozilla.org/security/advisories/mfsa2025-18/
- https://www.mozilla.org/security/advisories/mfsa2025-14/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1946004
