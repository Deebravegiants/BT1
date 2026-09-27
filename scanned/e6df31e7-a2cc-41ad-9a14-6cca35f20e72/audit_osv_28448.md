# [C] Unauthorized access to GET/SET of Slack Bot Tokens in Danswer

## Summary
Severity: Critical
Advisory: CVE-2024-32881
Aliases: GHSA-xr9w-3ggr-hr6j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-26
Source: https://osv.dev/vulnerability/CVE-2024-32881
Type: osv

## Details
Danswer is the AI Assistant connected to company's docs, apps, and people. Danswer is vulnerable to unauthorized access to GET/SET of Slack Bot Tokens. Anyone with network access can steal slack bot tokens and set them. This implies full compromise of the customer's slack bot, leading to internal Slack access. This issue was patched in version 3.63.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32881.json
- https://github.com/danswer-ai/danswer/security/advisories/GHSA-xr9w-3ggr-hr6j
- https://nvd.nist.gov/vuln/detail/CVE-2024-32881
- https://github.com/danswer-ai/danswer/commit/89ff07a96b41be9e05256bd252105be233f4d28a
- https://github.com/danswer-ai/danswer/commit/bd7e21a6388775e850d6f716675a893c72881e56
