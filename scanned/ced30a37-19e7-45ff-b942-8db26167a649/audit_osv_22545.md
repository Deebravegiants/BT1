# [H] OS Command Injection in mailcow

## Summary
Severity: High
Advisory: CVE-2022-31138
Aliases: GHSA-vx9w-h33p-5vhc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-11
Source: https://osv.dev/vulnerability/CVE-2022-31138
Type: osv

## Details
mailcow is a mailserver suite. Prior to mailcow-dockerized version 2022-06a, an extended privilege vulnerability can be exploited by manipulating the custom parameters regexmess, skipmess, regexflag, delete2foldersonly, delete2foldersbutnot, regextrans2, pipemess, or maxlinelengthcmd to execute arbitrary code. Users should update their mailcow instances with the `update.sh` script in the mailcow root directory to 2022-06a or newer to receive a patch for this issue. As a temporary workaround, the Syncjob ACL can be removed from all mailbox users, preventing changes to those settings.

## References
- https://github.com/mailcow/mailcow-dockerized/releases/tag/2022-06a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31138.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-vx9w-h33p-5vhc
- https://nvd.nist.gov/vuln/detail/CVE-2022-31138
- https://github.com/mailcow/mailcow-dockerized/commit/d373164e13a14e058f82c9f1918a5612f375a9f9
- https://github.com/ly1g3/Mailcow-CVE-2022-31138
