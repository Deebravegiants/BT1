# [H] BigBlueButton: Exposed ClamAV port enables Denial of Service

## Summary
Severity: High
Advisory: CVE-2026-27466
Aliases: GHSA-wmhx-qw2p-w6gc
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27466
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. In versions 3.0.21 and below, the official documentation for "Server Customization" on Support for ClamAV as presentation file scanner contains instructions that leave a BBB server vulnerable for Denial of Service. The flawed command exposes both ports (3310 and 7357) to the internet. A remote attacker can use this to send complex or large documents to clamd and waste server resources, or shutdown the clamd process. The clamd documentation explicitly warns about exposing this port. Enabling ufw (ubuntu firewall) during install does not help, because Docker routes container traffic through the nat table, which is not managed or restricted by ufw. Rules installed by ufw in the filter table have no effect on docker traffic. In addition, the provided example also mounts /var/bigbluebutton with write permissions into the container, which should not be required. Future vulnerabilities in clamd may allow attackers to manipulate files in that folder. Users are unaffected unless they have opted in to follow the extra instructions from BigBlueButton's documentation. This issue has been fixed in version 3.0.22.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27466.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-wmhx-qw2p-w6gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27466
- https://github.com/bigbluebutton/bigbluebutton/commit/f3d33d94a9682e87c7d41f55700b19d61e1ab8b4
