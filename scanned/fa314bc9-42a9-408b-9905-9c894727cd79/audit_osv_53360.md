# [M] CVE-2022-40959

## Summary
Severity: Medium
Advisory: CVE-2022-40959
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-40959
Type: osv

## Details
During iframe navigation, certain pages did not have their FeaturePolicy fully initialized leading to a bypass that leaked device permissions into untrusted subdocuments. This vulnerability affects Firefox ESR < 102.3, Thunderbird < 102.3, and Firefox < 105.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-41/
- https://www.mozilla.org/security/advisories/mfsa2022-42/
- https://www.mozilla.org/security/advisories/mfsa2022-40/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1782211
