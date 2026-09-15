# [M] Zulip Server public data export contains attachments that are non-public

## Summary
Severity: Medium
Advisory: CVE-2022-31134
Aliases: GHSA-58pm-88xp-7x9m
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-07-12
Source: https://osv.dev/vulnerability/CVE-2022-31134
Type: osv

## Details
Zulip is an open-source team collaboration tool. Zulip Server versions 2.1.0 above have a user interface tool, accessible only to server owners and server administrators, which provides a way to download a "public data" export. While this export is only accessible to administrators, in many configurations server administrators are not expected to have access to private messages and private streams. However, the "public data" export which administrators could generate contained the attachment contents for all attachments, even those from private messages and streams. Zulip Server version 5.4 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31134.json
- https://github.com/zulip/zulip/security/advisories/GHSA-58pm-88xp-7x9m
- https://nvd.nist.gov/vuln/detail/CVE-2022-31134
- https://blog.zulip.com/2022/07/12/zulip-cloud-data-exports
- https://blog.zulip.com/2022/07/12/zulip-server-5-4-security-release
