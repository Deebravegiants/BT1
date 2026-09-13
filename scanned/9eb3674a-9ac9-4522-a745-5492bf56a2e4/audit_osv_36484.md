# [M] CrawlChat's Discord Bot has a Knowledge Permission vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-23875
Aliases: GHSA-f484-62p4-6w4p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23875
Type: osv

## Details
CrawlChat is an open-source, AI-powered platform that transforms technical documentation into intelligent chatbots. Prior to version 0.0.8, a non-existing permission check for the CrawlChat's Discord bot allows non-manage guild users to put malicious content onto the collection knowledge base. Usually, admin / mods of a Discord guild use the `jigsaw` emoji to save a specific message (chain) onto the collection's knowledge base of CrawlChat. Unfortunately an permission check (for e.g. MANAGE_SERVER; MANAGE_MESSAGES etc.) was not done, allowing normal users of the guild to information to the knowledge base. With targeting specific parts that are commonly asked, users can manipulate the content given out by the bot (on all integrations), to e.g. redirect users to a malicious site, or send information to a malicious user. Version 0.0.8 patches the issue.

## References
- https://github.com/crawlchat/crawlchat/releases/tag/v0.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23875.json
- https://github.com/crawlchat/crawlchat/security/advisories/GHSA-f484-62p4-6w4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-23875
- https://github.com/crawlchat/crawlchat/commit/f90ebb93c6a830f6cf609d683f6425af8434573a
