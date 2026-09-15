# [H] Open WebUI: Cross-origin postMessage confirmation bypass via action:submit

## Summary
Severity: High
Advisory: GHSA-3vv5-8xxp-4f55
CVE: CVE-2026-54007
CWE: CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-3vv5-8xxp-4f55
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.9.6

## Details
### Summary

The chat message listener allows non-same-origin `input:prompt` and `action:submit` messages, so an external site can set prompt text and trigger `submitPrompt()` in an authenticated victim session. I validated this with a cross-origin attacker page that auto-posted messages and caused unauthorized `POST /api/v1/chats/new` and `POST /api/chat/completions` requests containing attacker-controlled prompts. This enables cross-site forced actions and model/tool execution under victim privileges without consent.

### Details

The chat page's window message listener in `src/lib/components/chat/Chat.svelte` processes message types including `input:prompt` and `action:submit` without adequately enforcing same-origin restrictions. Based on code around lines ~597-616, input text is set directly from `event.data.text`; `action:submit` proceeds to `submitPrompt()` on the current prompt. The logic does not apply a strict origin allowlist and permits non-same-origin control of the chat input and submission flow, leading to cross-origin command execution in the victim's authenticated UI context. As a result, backend API calls (e.g., `POST /api/v1/chats/new`, `POST /api/chat/completions`) are sent under victim credentials.

Normally, via the `input:prompt:submit` postMessage type, this results in a "Confirm Prompt from Embed" confirmation dialog:

https://github.com/open-webui/open-webui/blob/9bd84258d09eefe7bf975878fb0e31a5dadfe0f8/src/lib/components/chat/Chat.svelte#L604-L622

However, combining the two other types, it is possible to achieve the same effect without this confirmation:

https://github.com/open-webui/open-webui/blob/9bd84258d09eefe7bf975878fb0e31a5dadfe0f8/src/lib/components/chat/Chat.svelte#L584-L602

### PoC

1. Set up a local Open WebUI instance and log in to it, making sure a model is configured
2. Host the following HTML anywhere and visit it (optionally change http://127.0.0.1:14000 to your instance Base URL):

```html
<h1>Click anywhere</h1>
<script>
  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }
  
  onclick = async () => {
    w = window.open('http://127.0.0.1:14000');
    await sleep(2000);
    w.postMessage({ type: 'input:prompt', text: "INJECTED PROMPT" }, '*');
    await sleep(500);
    w.postMessage({ type: 'action:submit' }, '*');
  }
</script>
```

3. Click anywhere on the page, then notice without further interaction the "INJECTED PROMPT" is executed on the Open WebUI instance

<img width="874" height="264" alt="image" src="https://github.com/user-attachments/assets/244d9015-0dbf-47e0-a30e-1c2fbbde5e58" />

### Impact

Conditions required: The victim must be authenticated to Open WebUI in the browser (token cookie present).

This issue enables cross-site forced actions under the victim's identity. An attacker can silently inject prompts and trigger model/tool execution (e.g., code interpreter, web search, retrieval, terminal/tool servers) as the victim without confirmation.

### Original Agent Report

<img width="400" alt="app aikido dev_ai-pentests_projects_116389_assessments_019d67d4-81c8-7dd2-bb9e-0a4a774b2c78_issues_sidebarIssue=20439940 (4)" src="https://github.com/user-attachments/assets/7b6521ed-d08b-446d-a918-103523d08a1e" />

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-3vv5-8xxp-4f55
- https://nvd.nist.gov/vuln/detail/CVE-2026-54007
- https://github.com/advisories/GHSA-3vv5-8xxp-4f55
- https://github.com/open-webui/open-webui
- https://github.com/pypa/advisory-database/tree/main/vulns/open-webui/PYSEC-2026-2695.yaml
- https://pypi.org/project/open-webui
