# [H] CVE-2023-32215

## Summary
Severity: High
Advisory: CVE-2023-32215
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-32215
Type: osv

## Details
Mozilla developers and community members Gabriele Svelto, Andrew Osmond, Emily McDonough, Sebastian Hengst, Andrew McCreight and the Mozilla Fuzzing Team reported memory safety bugs present in Firefox 112 and Firefox ESR 102.10. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 113, Firefox ESR < 102.11, and Thunderbird < 102.11.

## References
- https://security.gentoo.org/glsa/202312-03
- https://security.gentoo.org/glsa/202401-10
- https://www.mozilla.org/security/advisories/mfsa2023-16/
- https://www.mozilla.org/security/advisories/mfsa2023-17/
- https://www.mozilla.org/security/advisories/mfsa2023-18/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1540883%2C1751943%2C1814856%2C1820210%2C1821480%2C1827019%2C1827024%2C1827144%2C1827359%2C1830186
