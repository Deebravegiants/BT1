# [H] CVE-2022-34481

## Summary
Severity: High
Advisory: CVE-2022-34481
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-34481
Type: osv

## Details
In the <code>nsTArray_Impl::ReplaceElementsAt()</code> function, an integer overflow could have occurred when the number of elements to replace was too large for the container. This vulnerability affects Firefox < 102, Firefox ESR < 91.11, Thunderbird < 102, and Thunderbird < 91.11.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-24/
- https://www.mozilla.org/security/advisories/mfsa2022-25/
- https://www.mozilla.org/security/advisories/mfsa2022-26/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1497246
