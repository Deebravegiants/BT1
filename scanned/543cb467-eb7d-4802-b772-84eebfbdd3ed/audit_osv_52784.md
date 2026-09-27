# [M] CVE-2022-1197

## Summary
Severity: Medium
Advisory: CVE-2022-1197
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-1197
Type: osv

## Details
When importing a revoked key that specified key compromise as the revocation reason, Thunderbird did not update the existing copy of the key that was not yet revoked, and the existing key was kept as non-revoked. Revocation statements that used another revocation reason, or that didn't specify a revocation reason, were unaffected. This vulnerability affects Thunderbird < 91.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1754985
