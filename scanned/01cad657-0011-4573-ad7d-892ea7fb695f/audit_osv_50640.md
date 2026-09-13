# [M] CVE-2020-26958

## Summary
Severity: Medium
Advisory: CVE-2020-26958
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26958
Type: osv

## Details
Firefox did not block execution of scripts with incorrect MIME types when the response was intercepted and cached through a ServiceWorker. This could lead to a cross-site script inclusion vulnerability, or a Content Security Policy bypass. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1669355
