# [M] CyberChef’s pretty-recipe parser vulnerable to client-side ReDoS / CPU exhaustion when parsing a malformed #recipe= URL

## Summary
Severity: Medium
Advisory: CVE-2026-72912
Aliases: GHSA-w74r-jxjh-gwr6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72912
Type: osv

## Details
CyberChef is a web app for encryption, encoding, compression, and data analysis. Prior to 11.3.0, CyberChef's pretty-recipe parser in src/core/Utils.mjs can exhaust client-side CPU when a malformed #recipe= URL fragment containing a large number of unmatched quote characters reaches Utils.parseRecipeConfig(). The function synchronously applies a complex global regular expression that may perform heavy backtracking before rejecting the input, causing the victim's browser tab to freeze during startup for seconds or longer. No code execution, data exfiltration, or privilege escalation occurs. This issue is fixed in version 11.3.0.

## References
- https://github.com/gchq/CyberChef/releases/tag/v11.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72912.json
- https://github.com/gchq/CyberChef/security/advisories/GHSA-w74r-jxjh-gwr6
- https://nvd.nist.gov/vuln/detail/CVE-2026-72912
- https://github.com/gchq/CyberChef/commit/f77ddf489050b339faa978bb28da954bafd289ae
- https://github.com/gchq/CyberChef/pull/2687
