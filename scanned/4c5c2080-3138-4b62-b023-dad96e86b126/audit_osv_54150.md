# [M] CVE-2023-4046

## Summary
Severity: Medium
Advisory: CVE-2023-4046
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-4046
Type: osv

## Details
In some circumstances, a stale value could have been used for a global variable in WASM JIT analysis. This resulted in incorrect compilation and a potentially exploitable crash in the content process. This vulnerability affects Firefox < 116, Firefox ESR < 102.14, and Firefox ESR < 115.1.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00010.html
- https://www.debian.org/security/2023/dsa-5464
- https://www.debian.org/security/2023/dsa-5469
- https://www.mozilla.org/security/advisories/mfsa2023-29/
- https://www.mozilla.org/security/advisories/mfsa2023-30/
- https://www.mozilla.org/security/advisories/mfsa2023-31/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1837686
