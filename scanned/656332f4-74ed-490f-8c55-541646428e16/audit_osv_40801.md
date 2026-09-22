# [H] PraisonAI: SSRF via redirect-following in praisonaiagents web_crawl

## Summary
Severity: High
Advisory: CVE-2026-55525
Aliases: GHSA-5r34-2g38-6569, PYSEC-2026-3898
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-55525
Type: osv

## Details
PraisonAI is a multi-agent teams system. Prior to praisonaiagents 1.6.58, the web_crawl function validates only the initial URL before _crawl_with_httpx uses httpx.Client(follow_redirects=True). Redirect targets are not revalidated, so an attacker who influences a crawl target can redirect a public URL to loopback, private network, or cloud metadata services while ALLOW_LOCAL_CRAWL remains disabled. The fetched internal response is returned to the agent context. This issue is fixed in version 1.6.58.

## References
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55525.json
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5r34-2g38-6569
- https://nvd.nist.gov/vuln/detail/CVE-2026-55525
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
