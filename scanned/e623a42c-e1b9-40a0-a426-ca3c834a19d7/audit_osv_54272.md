# [H] CVE-2023-4583

## Summary
Severity: High
Advisory: CVE-2023-4583
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-09-11
Source: https://osv.dev/vulnerability/CVE-2023-4583
Type: osv

## Details
When checking if the Browsing Context had been discarded in `HttpBaseChannel`, if the load group was not available then it was assumed to have already been discarded which was not always the case for private channels after the private session had ended. This vulnerability affects Firefox < 117, Firefox ESR < 115.2, and Thunderbird < 115.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-34/
- https://www.mozilla.org/security/advisories/mfsa2023-36/
- https://www.mozilla.org/security/advisories/mfsa2023-38/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1842030
