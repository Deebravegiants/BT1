# [M] CVE-2023-0547

## Summary
Severity: Medium
Advisory: CVE-2023-0547
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-0547
Type: osv

## Details
OCSP revocation status of recipient certificates was not checked when sending S/Mime encrypted email, and revoked certificates would be accepted. Thunderbird versions from 68 to 102.9.1 were affected by this bug. This vulnerability affects Thunderbird < 102.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1811298
