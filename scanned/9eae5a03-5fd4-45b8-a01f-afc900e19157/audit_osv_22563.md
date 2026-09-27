# [M] CVE-2022-31746

## Summary
Severity: Medium
Advisory: CVE-2022-31746
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31746
Type: osv

## Details
Internal URLs are protected by a secret UUID key, which could have been leaked to web page through the Referrer header. This vulnerability affects Firefox for iOS < 102.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31746.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-31746
- https://www.mozilla.org/security/advisories/mfsa2022-27/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1654416
