# [M] CVE-2023-29549

## Summary
Severity: Medium
Advisory: CVE-2023-29549
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-29549
Type: osv

## Details
Under certain circumstances, a call to the <code>bind</code> function may have resulted in the incorrect realm. This may have created a vulnerability relating to JavaScript-implemented sandboxes such as SES. This vulnerability affects Firefox for Android < 112, Firefox < 112, and Focus for Android < 112.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29549.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29549
- https://www.mozilla.org/security/advisories/mfsa2023-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1823042
