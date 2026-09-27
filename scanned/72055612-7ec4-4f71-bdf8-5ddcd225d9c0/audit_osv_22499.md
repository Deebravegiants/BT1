# [M] Improper privilege management - Anyone can view room settings in GreenLight

## Summary
Severity: Medium
Advisory: CVE-2022-31039
Aliases: GHSA-phh8-3v6v-7498
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-27
Source: https://osv.dev/vulnerability/CVE-2022-31039
Type: osv

## Details
Greenlight is a simple front-end interface for your BigBlueButton server. In affected versions an attacker can view any room's settings even though they are not authorized to do so. Only the room owner and administrator should be able to view a room's settings. This issue has been patched in release version 2.12.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31039.json
- https://github.com/bigbluebutton/greenlight/security/advisories/GHSA-phh8-3v6v-7498
- https://nvd.nist.gov/vuln/detail/CVE-2022-31039
- https://github.com/bigbluebutton/greenlight/pull/3508
