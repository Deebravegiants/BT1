# [M] CVE-2023-0430

## Summary
Severity: Medium
Advisory: CVE-2023-0430
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-0430
Type: osv

## Details
Certificate OCSP revocation status was not checked when verifying S/Mime signatures. Mail signed with a revoked certificate would be displayed as having a valid signature. Thunderbird versions from 68 to 102.7.0 were affected by this bug. This vulnerability affects Thunderbird < 102.7.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-04/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1769000
