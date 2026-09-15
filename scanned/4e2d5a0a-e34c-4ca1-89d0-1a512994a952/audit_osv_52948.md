# [C] CVE-2022-22759

## Summary
Severity: Critical
Advisory: CVE-2022-22759
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22759
Type: osv

## Details
If a document created a sandboxed iframe without <code>allow-scripts</code>, and subsequently appended an element to the iframe's document that e.g. had a JavaScript event handler - the event handler would have run despite the iframe's sandbox. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1739957
