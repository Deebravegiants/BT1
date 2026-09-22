# [M] CVE-2023-29544

## Summary
Severity: Medium
Advisory: CVE-2023-29544
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-29544
Type: osv

## Details
If multiple instances of resource exhaustion occurred at the incorrect time, the garbage collector could have caused memory corruption and a potentially exploitable crash. This vulnerability affects Firefox for Android < 112, Firefox < 112, and Focus for Android < 112.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29544.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29544
- https://www.mozilla.org/security/advisories/mfsa2023-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1818781
