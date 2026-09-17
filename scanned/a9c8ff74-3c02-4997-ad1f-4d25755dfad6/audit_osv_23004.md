# [M] Nextcloud Talk guests can continue to receive video streams from call after being removed from a conversation

## Summary
Severity: Medium
Advisory: CVE-2022-41971
Aliases: GHSA-wx6w-xpg9-6fv4
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-01
Source: https://osv.dev/vulnerability/CVE-2022-41971
Type: osv

## Details
Nextcould Talk android is a video and audio conferencing app for Nextcloud. Prior to versions 12.2.8, 13.0.10, 14.0.6, and 15.0.0, guests can continue to receive video streams from a call after being removed from a conversation. An attacker would be able to see videos on a call in a public conversation after being removed from that conversation, provided that they were removed while being in the call. Versions 12.2.8, 13.0.10, 14.0.6, and 15.0.0 contain patches for the issue. No known workarounds are available.

## References
- https://hackerone.com/reports/1706248
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41971.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wx6w-xpg9-6fv4
- https://nvd.nist.gov/vuln/detail/CVE-2022-41971
- https://github.com/nextcloud/spreed/pull/7974
