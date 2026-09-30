# [M] Grafana API IDOR

## Summary
Severity: Medium
Advisory: GHSA-63g3-9jq3-mccv
CVE: CVE-2022-21713
CWE: CWE-639, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-63g3-9jq3-mccv
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=5.0.0-beta1 <7.5.15
- Go: `github.com/grafana/grafana` — affected >=8.0.0 <8.3.5

## Details
Today we are releasing Grafana 8.3.5 and 7.5.14. This patch release includes MEDIUM severity security fix for Grafana Teams API IDOR.

Release v.8.3.5, only containing security fixes:

- [Download Grafana 8.3.5](https://grafana.com/grafana/download/8.3.5)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-8-3-5/)

Release v.7.5.15, only containing security fixes:

- [Download Grafana 7.5.15](https://grafana.com/grafana/download/7.5.15)
- [Release notes](https://grafana.com/docs/grafana/latest/release-notes/release-notes-7-5-15/)

## Teams API IDOR([CVE-2022-21713](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-21713))

On Jan. 18, an external security researcher, Kürşad ALSAN from [NSPECT.IO](https://www.nspect.io) ([@nspectio](https://twitter.com/nspectio) on Twitter), contacted Grafana to disclose an IDOR (Insecure Direct Object Reference) vulnerability on Grafana Teams APIs.

We believe that this vulnerability is rated at CVSS 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N).  

### Impact

This vulnerability only impacts the following API endpoints:

- `/teams/:teamId` - an authenticated attacker can view unintended data by querying for the specific team ID.
- `/teams/:search` - an authenticated attacker can search for teams and see the total number of available teams, including for those teams that the user does not have access to.
- `/teams/:teamId/members` - when editors_can_admin flag is enabled, an authenticated attacker can see unintended data by querying for the specific team ID.

### Affected versions with MEDIUM severity 
All Grafana >=5.0.0-beta1 versions are affected by this vulnerability.

### Solutions and mitigations

All installations after Grafana v5.0.0-beta1 should be upgraded as soon as possible.

Appropriate patches have been applied to [Grafana Cloud](https://grafana.com/cloud) and as always, we closely coordinated with all cloud providers licensed to offer Grafana Pro. They have received early notification under embargo and confirmed that their offerings are secure at the time of this announcement. This is applicable to Amazon Managed Grafana.

### Timeline and postmortem

Here is a detailed timeline starting from when we originally learned of the issue. All times in UTC.

- 2022-01-18 05:000 Issue submitted by external researcher
- 2022-01-21 17:45 Issue escalated and the vulnerability confirmed reproducible
- 2022-01-24 13:37 CVE requested
- 2022-01-24 14:40 Private release planned for 2022-01-25, and public release planned for 2022-02-01.
- 2022-01-24 17:00 PR with fix opened
- 2022-01-24 19:00 GitHub has issued CVE-2022-21713 
- 2022-01-25 12:00 Private release
- 2022-02-01 12:00 During public release process, we realized that private 7.x release was incomplete. Abort public release, send second private release to customers using 7.x
- 2022-02-08 13:00 Public release

### Acknowledgements
We would like to thank Kürşad ALSAN from [NSPECT.IO](https://www.nspect.io) ([@nspectio](https://twitter.com/nspectio) on Twitter) for responsibly disclosing the vulnerability.

### Reporting security issues

If you think you have found a security vulnerability, please send a report to security@grafana.com. This address can be used for all of Grafana Labs' open source and commercial products (including, but not limited to Grafana, Grafana Cloud, Grafana Enterprise, and grafana.com). We can accept only vulnerability reports at this address. We would prefer that you encrypt your message to us by using our PGP key. The key fingerprint is

F988 7BEA 027A 049F AE8E 5CAA D125 8932 BE24 C5CA

The key is available from keyserver.ubuntu.com.

### Security announcements

We maintain a [security category](https://community.grafana.com/c/support/security-announcements) on our blog, where we will always post a summary, remediation, and mitigation details for any patch containing security fixes.

You can also subscribe to our [RSS feed](https://grafana.com/tags/security/index.xml).

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-63g3-9jq3-mccv
- https://nvd.nist.gov/vuln/detail/CVE-2022-21713
- https://github.com/grafana/grafana/pull/45083
- https://github.com/grafana/grafana
- https://grafana.com/blog/2022/02/08/grafana-7.5.15-and-8.3.5-released-with-moderate-severity-security-fixes
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2PFW6Q2LXXWTFRTMTRN4ZGADFRQPKJ3D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/36GUEPA5TPSC57DZTPYPBL6T7UPQ2FRH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HLAQRRGNSO5MYCPAXGPH2OCSHOGHSQMQ
- https://security.netapp.com/advisory/ntap-20220303-0005
