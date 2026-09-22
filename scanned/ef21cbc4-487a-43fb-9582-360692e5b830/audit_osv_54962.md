# [H] CVE-2024-7525

## Summary
Severity: High
Advisory: CVE-2024-7525
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-08-06
Source: https://osv.dev/vulnerability/CVE-2024-7525
Type: osv

## Details
It was possible for a web extension with minimal permissions to create a `StreamFilter` which could be used to read and modify the response body of requests on any site. This vulnerability affects Firefox < 129, Firefox ESR < 115.14, Firefox ESR < 128.1, Thunderbird < 128.1, and Thunderbird < 115.14.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-35/
- https://www.mozilla.org/security/advisories/mfsa2024-37/
- https://www.mozilla.org/security/advisories/mfsa2024-38/
- https://www.mozilla.org/security/advisories/mfsa2024-33/
- https://www.mozilla.org/security/advisories/mfsa2024-34/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1909298
