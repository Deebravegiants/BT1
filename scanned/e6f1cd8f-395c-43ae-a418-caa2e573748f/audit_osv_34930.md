# [M] Nextcloud Calendar app used predictable proposal participant tokens

## Summary
Severity: Medium
Advisory: CVE-2025-66511
Aliases: GHSA-whm3-vv55-gf27
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66511
Type: osv

## Details
Nextcloud Calendar is a calendar app for Nextcloud. Prior to 6.0.3, the Calendar app generates participant tokens for meeting proposals using a hash function, allowing an attacker to compute valid participant tokens, which allowed them to request details and submit dates in meeting proposals. The tokens are not purely random generated. This vulnerability is fixed in 6.0.3.

## References
- https://hackerone.com/reports/3385434
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66511.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-whm3-vv55-gf27
- https://nvd.nist.gov/vuln/detail/CVE-2025-66511
- https://github.com/nextcloud/calendar/commit/8de14ae87f321f5f09280d9895a27d54d24f33fb
- https://github.com/nextcloud/calendar/pull/7659
