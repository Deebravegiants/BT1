# [C] Core Bot is Leaking Sensitive Credentials in Logs, Errors, and Messages

## Summary
Severity: Critical
Advisory: CVE-2025-65957
Aliases: GHSA-42j6-x28v-38r8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:H/VI:H/VA:H/SC:L/SI:H/SA:L)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-65957
Type: osv

## Details
Core Bot Is an Open Source discord bot made for maple hospital servers. Prior to commit dffe050, the API keys (SUPABASE_API_KEY, TOKEN) are loaded using environment variables, but there are cases in code (error handling, summaries, webhooks) where configuration summaries may inadvertently leak sensitive data (e.g., by failing to redact data in summary embeds or logs). This issue has been patched via commit dffe050.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65957.json
- https://github.com/Intercore-Productions/Core-Bot/security/advisories/GHSA-42j6-x28v-38r8
- https://nvd.nist.gov/vuln/detail/CVE-2025-65957
- https://github.com/Intercore-Productions/Core-Bot/commit/dffe050d565a580edfcd0242efa45da88ab31260
