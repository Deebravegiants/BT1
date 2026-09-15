# [H] Directus's webhook trigger flows can leak sensitive data

## Summary
Severity: High
Advisory: GHSA-fm3h-p9wm-h74h
CVE: CVE-2025-30353
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-26
Source: https://github.com/advisories/GHSA-fm3h-p9wm-h74h
Type: github-advisory

## Affected
- npm: `directus` — affected >=9.12.0 <11.5.0

## Details
### Describe the Bug

 In Directus, when a **Flow** with the "_Webhook_" trigger and the "_Data of Last Operation_" response body encounters a ValidationError thrown by a failed condition operation, the API response includes sensitive data. This includes environmental variables, sensitive API keys, user accountability information, and operational data.

This issue poses a significant security risk, as any unintended exposure of this data could lead to potential misuse.

![Image](https://github.com/user-attachments/assets/fb894347-cd10-4e79-9469-8fc1b2289794)
![Image](https://github.com/user-attachments/assets/a20337a2-005f-4cfd-ba30-fc5f579ed6c4)
![Image](https://github.com/user-attachments/assets/9b776248-4a20-46f0-92a4-3760d8e53df9)


### To Reproduce

**Steps to Reproduce:**
1. Create a Flow in Directus with:
   - Trigger: Webhook
   - Response Body: Data of Last Operation
2. Add a condition that is likely to fail.
3. Trigger the Flow with any input data that will fail the condition.
4. Observe the API response, which includes sensitive information like:
   - Environmental variables (`$env`)
   - Authorization headers
   - User details under `$accountability`
   - Previous operational data.

**Expected Behavior:**
In the event of a ValidationError, the API response should only contain relevant error messages and details, avoiding the exposure of sensitive data.

**Actual Behavior:**
The API response includes sensitive information such as:
- Environment keys (`FLOWS_ENV_ALLOW_LIST`)
- User accountability (`role`, `user`, etc.)
- Operational logs (`current_payments`, `$last`), which might contain private details.

## References
- https://github.com/directus/directus/security/advisories/GHSA-fm3h-p9wm-h74h
- https://nvd.nist.gov/vuln/detail/CVE-2025-30353
- https://github.com/directus/directus
