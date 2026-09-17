# [H] Flowise: Sensitive Data Leak in public-chatbotConfig 

## Summary
Severity: High
Advisory: GHSA-4jpm-cgx2-8h37
CVE: CVE-2026-41266
CWE: CWE-200, CWE-522, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-4jpm-cgx2-8h37
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary

`/api/v1/public-chatbotConfig/:id `ep exposes sensitive data including API keys, HTTP authorization headers and internal configuration without any authentication. An attacker with knowledge just of a chatflow UUID can retrieve credentials stored in password type fields and HTTP headers, leading to credential theft and more.

### Details

Knowledge of chatflow UUID can be obtained from embedded chat widgets, referrer headers or logs and it's the only prerequest. 

`getSinglePublicChatbotConfig` function in `packages/server/src/services/chatflows/index.ts` returns the full **flowData** object without authorization check or data sanitization.

There is a comment as **"Safe as public endpoint as chatbotConfig doesn't contain sensitive credential"** but **flowData** does contain sensitive data such as:

`type: 'password'` fields are stored in plaintext (unstructuredAPIKey in S3File node).
HTTP Authorization headers in POST / GET Requests nodes.
Internal API endpoints and webhook URLs.

### PoC

- Add an S3 File node, set "File Processing Method" to "Unstructured".
- Enter an API key in "Unstructured API KEY" field or add a Requests Post node with Authorization header.
- Save the chatflow.

`curl -s "https://localhost/api/v1/public-chatbotConfig/{CHATFLOW_UUID}"`

Response:

```
{
  "flowData": "{...\"unstructuredAPIKey\":\"victim_key\"...\"requestsPostHeaders\":\"Bearer victim_token\"...}"
}
```

### Impact

Impacts all Flowise Cloud users with chatflows containing password type fields or any HTTP headers. And self hosted Flowise instances exposed to the internet.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-4jpm-cgx2-8h37
- https://nvd.nist.gov/vuln/detail/CVE-2026-41266
- https://github.com/FlowiseAI/Flowise
