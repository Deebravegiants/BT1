# [M] CVE-2023-23598

## Summary
Severity: Medium
Advisory: CVE-2023-23598
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-23598
Type: osv

## Details
Due to the Firefox GTK wrapper code's use of text/plain for drag data and GTK treating all text/plain MIMEs containing file URLs as being dragged a website could arbitrarily read a file via a call to `DataTransfer.setData`. This vulnerability affects Firefox < 109, Firefox ESR < 102.7, and Thunderbird < 102.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-01/
- https://www.mozilla.org/security/advisories/mfsa2023-02/
- https://www.mozilla.org/security/advisories/mfsa2023-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1800425
