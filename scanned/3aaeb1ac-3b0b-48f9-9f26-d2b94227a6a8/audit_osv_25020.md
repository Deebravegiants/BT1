# [H] CVE-2023-29551

## Summary
Severity: High
Advisory: CVE-2023-29551
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-29551
Type: osv

## Details
Memory safety bugs present in Firefox 111. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox for Android < 112, Firefox < 112, and Focus for Android < 112.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29551.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29551
- https://www.mozilla.org/security/advisories/mfsa2023-13/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1763625%2C1814314%2C1815798%2C1815890%2C1819239%2C1819465%2C1819486%2C1819492%2C1819957%2C1820514%2C1820776%2C1821838%2C1822175%2C1823547
