# [C] Crawl4AI: Unauthenticated RCE via Chromium launch-argument injection in browser_config.extra_args

## Summary
Severity: Critical
Advisory: GHSA-r253-r9jw-qg44
CWE: CWE-88, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-r253-r9jw-qg44
Type: github-advisory

## Affected
- PyPI: `crawl4ai` — affected >=0 <0.9.0

## Details
### Summary

The Docker API server accepted a request-supplied `browser_config.extra_args`, which flowed into Chromium's launch arguments. An attacker could inject Chromium switches that replace a child-process launch command (`--utility-cmd-prefix`, `--renderer-cmd-prefix`, `--gpu-launcher`, `--browser-subprocess-path`) together with `--no-zygote`, causing Chromium to fork/exec an attacker-controlled command as the container's runtime user. The Docker API is unauthenticated by default, so a single request yields arbitrary command execution.

The earlier `extra_args` SSRF patch (0.8.9) used a denylist scoped to proxy/DNS flags; a denylist of launch switches is inherently incomplete, and these command-execution switches were not covered.

### Affected paths

`/crawl`, `/crawl/stream`, `/crawl/job` accepting a request `browser_config.extra_args`.

### Impact

Unauthenticated remote code execution as the container runtime user; full read/write of application data, mounted secrets, environment, and tokens, and out-of-band exfiltration independent of the HTTP response.

### Fix

0.9.0 establishes a trust boundary for request-supplied configuration: `extra_args` (along with other power fields such as `proxy`, `user_data_dir`, `cdp_url`, `init_scripts`) is a forbidden field for untrusted request bodies. Any request that sets `extra_args` is rejected with HTTP 400 rather than scrubbed against an always-incomplete denylist. In-process SDK callers (trusted) are unaffected.

### Workarounds

- Upgrade to the patched version (0.9.0).
- Enable authentication (`CRAWL4AI_API_TOKEN`) and restrict who can reach the API.
- Run the container with a restrictive seccomp profile and no ability to exec helper binaries.

### Credits

Y4tacker - reported the `--no-zygote` + `--utility-cmd-prefix` command-injection chain with a confirmed in-container PoC and an allowlist/reject recommendation.
UDU_RisePho (hoanggxyuuki) - independently reported the request-supplied Chromium launch-flag RCE class (`--renderer-cmd-prefix`), confirmed still reproducing on 0.8.9.

## References
- https://github.com/unclecode/crawl4ai/security/advisories/GHSA-r253-r9jw-qg44
- https://github.com/unclecode/crawl4ai
