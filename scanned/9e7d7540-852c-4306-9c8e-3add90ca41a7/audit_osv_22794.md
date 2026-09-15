# [M] Last video frame is still sent after video is disabled in a call in Nextcloud Talk

## Summary
Severity: Medium
Advisory: CVE-2022-39212
Aliases: GHSA-wq3g-2x46-q2gv
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-09-16
Source: https://osv.dev/vulnerability/CVE-2022-39212
Type: osv

## Details
Nextcloud Talk is an open source chat, video & audio calls client for the Nextcloud platform. In affected versions an attacker could see the last video frame of any participant who has video disabled but a camera selected. It is recommended that the Nextcloud Talk app is upgraded to 13.0.8 or 14.0.4. Users unable to upgrade should select "None" as camera before joining the call.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39212.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-wq3g-2x46-q2gv
- https://nvd.nist.gov/vuln/detail/CVE-2022-39212
- https://github.com/nextcloud/spreed/pull/7673
