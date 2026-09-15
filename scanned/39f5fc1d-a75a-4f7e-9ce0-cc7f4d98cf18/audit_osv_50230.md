# [M] CVE-2019-9816

## Summary
Severity: Medium
Advisory: CVE-2019-9816
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-9816
Type: osv

## Details
A possible vulnerability exists where type confusion can occur when manipulating JavaScript objects in object groups, allowing for the bypassing of security checks within these groups. *Note: this vulnerability has only been demonstrated with UnboxedObjects, which are disabled by default on all supported releases.*. This vulnerability affects Thunderbird < 60.7, Firefox < 67, and Firefox ESR < 60.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-13/
- https://www.mozilla.org/security/advisories/mfsa2019-14/
- https://www.mozilla.org/security/advisories/mfsa2019-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1536768
