# [H] CVE-2020-15669

## Summary
Severity: High
Advisory: CVE-2020-15669
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-01
Source: https://osv.dev/vulnerability/CVE-2020-15669
Type: osv

## Details
When aborting an operation, such as a fetch, an abort signal may be deleted while alerting the objects to be notified. This results in a use-after-free and we presume that with enough effort it could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 68.12 and Thunderbird < 68.12.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-37/
- https://www.mozilla.org/security/advisories/mfsa2020-40/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1656957
