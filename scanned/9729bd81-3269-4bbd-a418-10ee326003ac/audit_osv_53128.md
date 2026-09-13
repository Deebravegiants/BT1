# [M] CVE-2022-3032

## Summary
Severity: Medium
Advisory: CVE-2022-3032
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-3032
Type: osv

## Details
When receiving an HTML email that contained an <code>iframe</code> element, which used a <code>srcdoc</code> attribute to define the inner HTML document, remote objects specified in the nested document, for example images or videos, were not blocked. Rather, the network was accessed, the objects were loaded and displayed. This vulnerability affects Thunderbird < 102.2.1 and Thunderbird < 91.13.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-38/
- https://www.mozilla.org/security/advisories/mfsa2022-39/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1783831
