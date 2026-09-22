# [H] CVE-2020-6819

## Summary
Severity: High
Advisory: CVE-2020-6819
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-24
Source: https://osv.dev/vulnerability/CVE-2020-6819
Type: osv

## Details
Under certain conditions, when running the nsDocShell destructor, a race condition can cause a use-after-free. We are aware of targeted attacks in the wild abusing this flaw. This vulnerability affects Thunderbird < 68.7.0, Firefox < 74.0.1, and Firefox ESR < 68.6.1.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-6819
- https://www.mozilla.org/security/advisories/mfsa2020-11/
- https://www.mozilla.org/security/advisories/mfsa2020-14/
- https://usn.ubuntu.com/4335-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1620818
