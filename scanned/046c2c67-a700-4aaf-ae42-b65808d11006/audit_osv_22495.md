# [M] Federated editing allows iframing remote servers by default in richdocuments

## Summary
Severity: Medium
Advisory: CVE-2022-31024
Aliases: GHSA-94hr-7g4v-f53r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-06-02
Source: https://osv.dev/vulnerability/CVE-2022-31024
Type: osv

## Details
richdocuments is the repository for NextCloud Collabra, the app for Nextcloud Office collaboration. Prior to versions 6.0.0, 5.0.4, and 4.2.6, a user could be tricked into working against a remote Office by sending them a federated share. richdocuments versions 6.0.0, 5.0.4 and 4.2.6 contain a fix for this issue. There are currently no known workarounds available.

## References
- https://hackerone.com/reports/1210424
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31024.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-94hr-7g4v-f53r
- https://nvd.nist.gov/vuln/detail/CVE-2022-31024
- https://github.com/nextcloud/richdocuments/pull/2161
