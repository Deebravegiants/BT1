# [M] Exception logging in Sharepoint app reveals clear-text connection details

## Summary
Severity: Medium
Advisory: CVE-2022-39364
Aliases: GHSA-qpf5-jj85-36h5
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-10-27
Source: https://osv.dev/vulnerability/CVE-2022-39364
Type: osv

## Details
Nextcloud Server is the file server software for Nextcloud, a self-hosted productivity platform. In Nextcloud Server prior to versions 23.0.9 and 24.0.5 and Nextcloud Enterprise Server prior to versions 22.2.10.5, 23.0.9, and 24.0.5 an attacker reading `nextcloud.log` may gain knowledge of credentials to connect to a SharePoint service. Nextcloud Server versions 23.0.9 and 24.0.5 and Nextcloud Enterprise Server versions 22.2.10.5, 23.0.9, and 24.0.5 contain a patch for this issue. As a workaround, set `zend.exception_ignore_args = On` as an option in `php.ini`.

## References
- https://hackerone.com/reports/1652903
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39364.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qpf5-jj85-36h5
- https://nvd.nist.gov/vuln/detail/CVE-2022-39364
- https://github.com/nextcloud/sharepoint/issues/141
- https://github.com/nextcloud/server/pull/33689
