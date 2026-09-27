# [M] Ray dashboard DELETE endpoints allow unauthenticated browser-triggered DoS (Serve shutdown / job deletion)

## Summary
Severity: Medium
Advisory: GHSA-q5fh-2hc8-f6rq
CVE: CVE-2026-27482
CWE: CWE-306, CWE-396
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-q5fh-2hc8-f6rq
Type: github-advisory

## Affected
- PyPI: `ray` — affected >=0 <2.54.0

## Details
### Summary

  Ray’s dashboard HTTP server blocks browser-origin POST/PUT but does not cover DELETE, and key DELETE endpoints are unauthenticated by default. If the dashboard/agent is reachable (e.g., --dashboard-host=0.0.0.0), a web page via DNS rebinding or same-network access can
  issue DELETE requests that shut down Serve or delete jobs without user interaction. This is a drive-by availability impact.

  ### Details

  - Middleware: python/ray/dashboard/http_server_head.py#get_browsers_no_post_put_middleware only checks POST/PUT via is_browser_request (UA/Origin/Sec-Fetch heuristics). DELETE is not gated.
  - Endpoints lacking browser protection/auth by default:
      - python/ray/dashboard/modules/serve/serve_head.py: @routes.delete("/api/serve/applications/") calls serve.shutdown().
      - python/ray/dashboard/modules/job/job_head.py: @routes.delete("/api/jobs/{job_or_submission_id}").
      - python/ray/dashboard/modules/job/job_agent.py: @routes.delete("/api/job_agent/jobs/{job_or_submission_id}") (not wrapped with deny_browser_requests either).
  - Dashboard token auth is optional and off by default; binding to 0.0.0.0 is common for remote access.

  ### PoC

  Prereqs: dashboard reachable (e.g., ray start --head --dashboard-host=0.0.0.0), no token auth.

  1. Start Serve (or have jobs present).
  2. From any browser-reachable origin (DNS rebinding or same-LAN page), issue a DELETE fetch:

```  
fetch("http://<dashboard-host>:8265/api/serve/applications/", {
    method: "DELETE",
    headers: { "User-Agent": "Mozilla/5.0" }  // browsers set this automatically
  });
```

  Result: Serve shuts down.
  3) Similarly, delete jobs:

 ` fetch("http://<dashboard-host>:8265/api/jobs/<job_or_submission_id>", { method: "DELETE" });`
 ` fetch("http://<dashboard-agent>:52365/api/job_agent/jobs/<job_or_submission_id>", { method: "DELETE" });`

  Browsers will send the Mozilla UA and Origin/Sec-Fetch headers, but DELETE is not blocked by the middleware, so the requests succeed.

  ### Impact

  - Availability loss: Serve shutdown; job deletion. Triggerable via drive-by browser requests if the dashboard/agent ports are reachable and auth is disabled (default).
  - No code execution from this vector, but breaks isolation/trust assumptions for “developer-only” endpoints.
  
### Fix
The fix for this vulnerability is to update to Ray 2.54.0 or higher. 

Fix PR: https://github.com/ray-project/ray/pull/60526

## References
- https://github.com/ray-project/ray/security/advisories/GHSA-q5fh-2hc8-f6rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27482
- https://github.com/ray-project/ray/pull/60526
- https://github.com/ray-project/ray/commit/0fda8b824cdc9dc6edd763bb28dfd7d1cc9b02a4
- https://github.com/ray-project/ray
- https://github.com/ray-project/ray/releases/tag/ray-2.54.0
