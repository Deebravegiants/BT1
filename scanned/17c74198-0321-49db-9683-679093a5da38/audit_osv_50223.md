# [C] CVE-2019-9796

## Summary
Severity: Critical
Advisory: CVE-2019-9796
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9796
Type: osv

## Details
A use-after-free vulnerability can occur when the SMIL animation controller incorrectly registers with the refresh driver twice when only a single registration is expected. When a registration is later freed with the removal of the animation controller element, the refresh driver incorrectly leaves a dangling pointer to the driver's observer array. This vulnerability affects Thunderbird < 60.6, Firefox ESR < 60.6, and Firefox < 66.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-08/
- https://www.mozilla.org/security/advisories/mfsa2019-11/
- https://access.redhat.com/errata/RHSA-2019:0966
- https://access.redhat.com/errata/RHSA-2019:1144
- https://www.mozilla.org/security/advisories/mfsa2019-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1531277
