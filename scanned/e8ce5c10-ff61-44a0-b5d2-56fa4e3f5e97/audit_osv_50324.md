# [H] CVE-2020-12406

## Summary
Severity: High
Advisory: CVE-2020-12406
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2020-12406
Type: osv

## Details
Mozilla Developer Iain Ireland discovered a missing type check during unboxed objects removal, resulting in a crash. We presume that with enough effort that it could be exploited to run arbitrary code. This vulnerability affects Thunderbird < 68.9.0, Firefox < 77, and Firefox ESR < 68.9.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-20/
- https://www.mozilla.org/security/advisories/mfsa2020-21/
- https://www.mozilla.org/security/advisories/mfsa2020-22/
- https://usn.ubuntu.com/4421-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1639590
