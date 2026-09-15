# [C] Media transport downgrade from the secure version (SRTP) to non-secure (RTP) in pjsip

## Summary
Severity: Critical
Advisory: CVE-2022-39269
Aliases: GHSA-wx5m-cj97-4wwg
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/CVE-2022-39269
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. When processing certain packets, PJSIP may incorrectly switch from using SRTP media transport to using basic RTP upon SRTP restart, causing the media to be sent insecurely. The vulnerability impacts all PJSIP users that use SRTP. The patch is available as commit d2acb9a in the master branch of the project and will be included in version 2.13. Users are advised to manually patch or to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39269.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-wx5m-cj97-4wwg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39269
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2023/dsa-5358
- https://github.com/pjsip/pjproject/commit/d2acb9af4e27b5ba75d658690406cec9c274c5cc
- https://lists.debian.org/debian-lts-announce/2023/02/msg00029.html
