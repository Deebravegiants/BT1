# [H] CVE-2022-26485

## Summary
Severity: High
Advisory: CVE-2022-26485
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26485
Type: osv

## Details
Removing an XSLT parameter during processing could have lead to an exploitable use-after-free. We have had reports of attacks in the wild abusing this flaw. This vulnerability affects Firefox < 97.0.2, Firefox ESR < 91.6.1, Firefox for Android < 97.3.0, Thunderbird < 91.6.2, and Focus < 97.3.0.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-26485
- https://www.mozilla.org/security/advisories/mfsa2022-09/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1758062
