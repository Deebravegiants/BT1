# [H] CVE-2023-25747

## Summary
Severity: High
Advisory: CVE-2023-25747
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-25747
Type: osv

## Details
A potential use-after-free in libaudio was fixed by disabling the AAudio backend when running on Android API below version 30.
*This bug only affects Firefox for Android. Other versions of Firefox are unaffected.* This vulnerability affects Firefox for Android < 110.1.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25747.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25747
- https://www.mozilla.org/security/advisories/mfsa2023-08/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1815801
