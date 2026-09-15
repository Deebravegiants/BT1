# [M] CKAN MCP Server: MQA server allowlist bypass via unanchored regex (`isValidMqaServer`)

## Summary
Severity: Medium
Advisory: GHSA-83x6-42hr-jc76
CVE: CVE-2026-73845
CWE: CWE-20, CWE-625, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-83x6-42hr-jc76
Type: github-advisory

## Affected
- npm: `@aborruso/ckan-mcp-server` — affected >=0 <0.4.112

## Details
## Summary

The `ckan_get_mqa_quality` and `ckan_get_mqa_quality_details` tools restrict their `server_url` argument to `dati.gov.it` via a regular expression. The regex is anchored only at the start and places no boundary after the host, so any URL whose host merely **begins with** `dati.gov.it` — or that uses `dati.gov.it` as URL *userinfo* before an `@` — passes validation while actually targeting an attacker-controlled host.

## Affected code

```js
// src/tools/quality.ts
const ALLOWED_SERVER_PATTERNS = [
  /^https?:\/\/(www\.)?dati\.gov\.it/i        // <-- no end anchor / host boundary
];
export function isValidMqaServer(serverUrl: string): boolean {
  return ALLOWED_SERVER_PATTERNS.some(pattern => pattern.test(serverUrl));
}
```

All of the following return `true`:

| URL | Real host |
|-----|-----------|
| `https://dati.gov.it.attacker.com/x` | `dati.gov.it.attacker.com` (attacker) |
| `http://dati.gov.it.evil.example/api` | `dati.gov.it.evil.example` (attacker) |
| `https://dati.gov.it@attacker.com/x` | `attacker.com` (userinfo trick) |

After passing this check, `server_url` flows into `getMqaQuality`/`getMqaQualityDetails`, which call `makeCkanRequest(serverUrl, "package_show", { id })`. The server therefore issues a request to the attacker-controlled host and returns its (parsed) response to the caller.

## Impact

- The intended "dati.gov.it only" trust boundary for the MQA tools is defeated; they can be driven against arbitrary external hosts.
- The attacker host receives the request (including the `dataset_id`) and controls the response body that is surfaced back to the model/user — enabling response spoofing and, in an agentic setting, indirect prompt-injection content delivered under the guise of a trusted-portal tool.
- Contributes to SSRF surface: while `makeCkanRequest` blocks private/internal IPs, this bypass removes the domain restriction that the code intends to enforce for these tools.

The `@`-userinfo variant is the most severe form because validation passes on a string whose *actual* host is fully attacker-chosen.

## Proof of concept

`poc/mqa-allowlist-poc.mjs` runs the verbatim regex over benign and malicious URLs:

```
accepted  expected_legit  url
true      true            https://dati.gov.it/opendata          <- legit
true      false           https://dati.gov.it.attacker.com/x    <- BYPASS
true      false           http://dati.gov.it.evil.example/api   <- BYPASS
true      false           https://dati.gov.it@attacker.com/x    <- BYPASS
```

## Remediation

Validate the parsed host, not the raw string. For example:

```js
function isValidMqaServer(serverUrl) {
  let u; try { u = new URL(serverUrl); } catch { return false; }
  if (u.protocol !== "https:") return false;
  const h = u.hostname.toLowerCase();
  return h === "dati.gov.it" || h === "www.dati.gov.it";
  // or: h === "dati.gov.it" || h.endsWith(".dati.gov.it")
}
```

Anchoring the regex end-to-end (`/^https:\/\/(www\.)?dati\.gov\.it(\/|$)/i`) also closes the suffix trick, but URL-parsing + exact host comparison is the robust fix and also neutralizes the `@`-userinfo variant.

## References
- https://github.com/ondata/ckan-mcp-server/security/advisories/GHSA-83x6-42hr-jc76
- https://nvd.nist.gov/vuln/detail/CVE-2026-73845
- https://github.com/ondata/ckan-mcp-server/commit/8e1522f9bbfa1f3b21550f17887f60f133e24151
- https://github.com/ondata/ckan-mcp-server
- https://github.com/ondata/ckan-mcp-server/releases/tag/v0.4.112
