# [M] CVE-2025-64084

## Summary
Severity: Medium
Advisory: CVE-2025-64084
Aliases: GHSA-4r9r-3r3q-jg44
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-11-14
Source: https://osv.dev/vulnerability/CVE-2025-64084
Type: osv

## Details
An authenticated SQL injection vulnerability exists in Cloudlog 2.7.5 and earlier. The vucc_details_ajax function in application/controllers/Awards.php does not properly sanitize the user-supplied Gridsquare POST parameter. This allows a remote, authenticated attacker to execute arbitrary SQL commands by injecting a malicious payload, which is then concatenated directly into a raw SQL query in the vucc_qso_details function.

## References
- https://github.com/magicbug/Cloudlog/releases/tag/2.7.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64084.json
- https://github.com/XY20130630/Cloudlog/security/advisories/GHSA-4r9r-3r3q-jg44
- https://nvd.nist.gov/vuln/detail/CVE-2025-64084
- https://github.com/magicbug/Cloudlog/commit/72a8c3d705c8629f60f64da9f37968417c980242
