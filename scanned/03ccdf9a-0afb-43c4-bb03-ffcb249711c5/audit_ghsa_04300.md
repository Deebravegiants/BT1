# [M] Langflow: Logout button does not clear session

## Summary
Severity: Medium
Advisory: GHSA-7hw8-6q6r-4276
CVE: CVE-2026-55423
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-7hw8-6q6r-4276
Type: github-advisory

## Affected
- PyPI: `langflow` — affected >=0 <1.7.1

## Details
### Summary
The logout button does not clear the session. The previous user stays logged in unless another user explicitly logs in.

### Details
Not in auto login mode. Hosted on localhost. `access_token_lf` remains present in both Local Storage and Cookies. `refresh_token_lf` remains present in Cookies.

**Root cause:** the `/logout` endpoint deleted the authentication cookies without matching the original `httponly`/`samesite`/`secure`/`domain` parameters, so the browser kept them; additionally the frontend did not clear the auth cookies on logout.

```
LANGFLOW_AUTO_LOGIN: "False"
LANGFLOW_SUPERUSER: <set>
LANGFLOW_SUPERUSER_PASSWORD: <set>
LANGFLOW_SECRET_KEY: <set>
LANGFLOW_NEW_USER_IS_ACTIVE: "False"
LANGFLOW_ENABLE_SUPERUSER_CLI: "False"
```

### PoC
Click Logout. Hit refresh to return to previous screen.

### Impact
Users on shared computers may falsely believe they have terminated their session.

### Patches
Fixed in **1.7.0** (PRs #10527 and #10528). The logout endpoint now deletes the auth cookies using the same parameters they were created with, and the frontend clears the auth cookies on logout. Upgrade to **1.7.0 or later**.

## References
- https://github.com/langflow-ai/langflow/security/advisories/GHSA-7hw8-6q6r-4276
- https://github.com/langflow-ai/langflow/pull/10527
- https://github.com/langflow-ai/langflow/pull/10528
- https://github.com/langflow-ai/langflow
