# [M] CVE-2024-8394

## Summary
Severity: Medium
Advisory: CVE-2024-8394
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-09-06
Source: https://osv.dev/vulnerability/CVE-2024-8394
Type: osv

## Details
When aborting the verification of an OTR chat session, an attacker could have caused a use-after-free bug leading to a potentially exploitable crash. This vulnerability affects Thunderbird < 128.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-43/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1895737
