# [M] CVE-2022-45403

## Summary
Severity: Medium
Advisory: CVE-2022-45403
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45403
Type: osv

## Details
Service Workers should not be able to infer information about opaque cross-origin responses; but timing information for cross-origin media combined with Range requests might have allowed them to determine the presence or length of a media file. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1762078
