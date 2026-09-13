# [M] CVE-2021-39195

## Summary
Severity: Medium
Advisory: CVE-2021-39195
Aliases: GHSA-mqv7-gxh4-r5vf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-39195
Type: osv

## Details
Misskey is an open source, decentralized microblogging platform. In affected versions a Server-Side Request Forgery vulnerability exists in "Upload from URL" and remote attachment handling. This could result in the disclosure of non-public information within the internal network. This has been fixed in 12.90.0. However, if you are using a proxy, you will need to take additional measures. As a workaround this exploit may be avoided by appropriately restricting access to private networks from the host where the application is running.

## References
- https://github.com/misskey-dev/misskey/blob/develop/CHANGELOG.md#12900-20210904
- https://github.com/misskey-dev/misskey/commit/e1a8b158e04ad567d92d8daf3cc0898ee18f1a2e
- https://github.com/misskey-dev/misskey/security/advisories/GHSA-mqv7-gxh4-r5vf
