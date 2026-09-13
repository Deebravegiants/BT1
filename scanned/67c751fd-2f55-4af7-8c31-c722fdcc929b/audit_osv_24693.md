# [M] Document content of files can be obtained through Collabora for files of other users

## Summary
Severity: Medium
Advisory: CVE-2023-25150
Aliases: GHSA-64xc-r58v-53gj
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/CVE-2023-25150
Type: osv

## Details
Nextcloud office/richdocuments is an office suit for the nextcloud server platform. In affected versions the Collabora integration can be tricked to provide access to any file without proper permission validation. As a result any user with access to Collabora can obtain the content of other users files. It is recommended that the Nextcloud Office App (Collabora Integration) is updated to 7.0.2 (Nextcloud 25), 6.3.2 (Nextcloud 24), 5.0.10 (Nextcloud 23), 4.2.9 (Nextcloud 21-22), or 3.8.7 (Nextcloud 15-20). There are no known workarounds for this issue.

## References
- https://hackerone.com/reports/1788222
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25150.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-64xc-r58v-53gj
- https://nvd.nist.gov/vuln/detail/CVE-2023-25150
- https://github.com/nextcloud/richdocuments/pull/2669
