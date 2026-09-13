# [H] CVE-2024-0605

## Summary
Severity: High
Advisory: CVE-2024-0605
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/CVE-2024-0605
Type: osv

## Details
Using a javascript: URI with a setTimeout race condition, an attacker can execute unauthorized scripts on top origin sites in urlbar. This bypasses security measures, potentially leading to arbitrary code execution or unauthorized actions within the user's loaded webpage. This vulnerability affects Focus for iOS < 122.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0605.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0605
- https://www.mozilla.org/security/advisories/mfsa2024-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1855575
