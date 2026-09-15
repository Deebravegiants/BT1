# [M] Improper Input Validation in kenny2automate

## Summary
Severity: Medium
Advisory: CVE-2023-22452
Aliases: GHSA-73j8-xrcr-q6j7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-01-02
Source: https://osv.dev/vulnerability/CVE-2023-22452
Type: osv

## Details
kenny2automate is a Discord bot. In the web interface for server settings, form elements were generated with Discord channel IDs as part of input names. Prior to commit a947d7c, no validation was performed to ensure that the channel IDs submitted actually belonged to the server being configured. Thus anyone who has access to the channel ID they wish to change settings for and the server settings panel for any server could change settings for the requested channel no matter which server it belonged to. Commit a947d7c resolves the issue and has been deployed to the official instance of the bot. The only workaround that exists is to disable the web config entirely by changing it to run on localhost. Note that a workaround is only necessary for those who run their own instance of the bot.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22452.json
- https://github.com/Kenny2github/kenny2automate/security/advisories/GHSA-73j8-xrcr-q6j7
- https://nvd.nist.gov/vuln/detail/CVE-2023-22452
- https://github.com/Kenny2github/kenny2automate/commit/a947d7ce408687b587c7e6dfd6026f7c4ee31ac2
