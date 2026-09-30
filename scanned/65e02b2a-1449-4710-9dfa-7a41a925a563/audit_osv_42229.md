# [H] Likeshop 3.0.5 Authenticated SQL Injection via adjustAccount Endpoint

## Summary
Severity: High
Advisory: CVE-2026-65707
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-65707
Type: osv

## Details
Likeshop through 3.0.5 contains an authenticated SQL injection vulnerability that allows admin-level users to extract arbitrary database contents by submitting unsanitized POST parameters to the adjustAccount endpoint. The adjustAccount method in UserLogic.php concatenates the money, integral, growth, and earnings parameters directly into Db::raw() SQL fragments without type casting, numeric validation, or parameter binding, enabling boolean-based binary-search extraction of credentials, PII, and session tokens via distinct success and failure response messages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65707
- https://www.vulncheck.com/advisories/likeshop-authenticated-sql-injection-via-adjustaccount-endpoint
- https://github.com/likeadmin-likeshop/likeshop
- https://gist.github.com/peoz14/794521dc40f5bb7e6a6ec6630d894be6
