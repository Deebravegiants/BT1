# [M] Craftplan < 0.5.1 Broken Access Control Information Disclosure via Settings API

## Summary
Severity: Medium
Advisory: CVE-2026-76876
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-76876
Type: osv

## Details
Craftplan before 0.5.1 contains a broken access control vulnerability that allows unauthenticated attackers to read sensitive credentials by exploiting an unconditional authorization policy on the Settings resource. Attackers can send a GET request to the settings API endpoint with a valid record ID to retrieve decrypted SMTP passwords, email API keys, and email API secrets due to the read policy using an always-allow authorization check that bypasses all identity verification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76876.json
- https://github.com/puemos/craftplan/releases/tag/v0.5.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-76876
- https://www.vulncheck.com/advisories/craftplan-broken-access-control-information-disclosure-via-settings-api
- https://github.com/puemos/craftplan/commit/317acd584b68887f592dc3b97f47703dd63b1bf
- https://github.com/puemos/craftplan
