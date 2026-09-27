# [H] Apache HertzBeat (incubating): RCE by parse http sitemap xml response

## Summary
Severity: High
Advisory: CVE-2025-24404
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-24404
Type: osv

## Details
XML Injection RCE by parse http sitemap xml response vulnerability in Apache HertzBeat.












The attacker needs to have an authenticated account with access, and add monitor parsed by xml, returned special content can trigger the XML parsing vulnerability.

This issue affects Apache HertzBeat (incubating): before 1.7.0.

Users are recommended to upgrade to version 1.7.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/09/06/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24404.json
- https://lists.apache.org/thread/4ydy3tqbpwmhl79mcj3pxwqz62nggrfd
- https://nvd.nist.gov/vuln/detail/CVE-2025-24404
