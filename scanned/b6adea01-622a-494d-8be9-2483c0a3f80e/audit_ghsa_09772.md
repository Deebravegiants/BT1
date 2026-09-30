# [H] Open WebUI has Broken Access Control in Tool Valves

## Summary
Severity: High
Advisory: GHSA-7429-hxcv-268m
CVE: CVE-2026-34222
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-7429-hxcv-268m
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.11

## Details
# Summary

## Broken Access Control in Tool Valves

Open WebUI supports function calling through "Tools". Function calling allows an LLM to reliably connect to external tools and interact with external APIs. Exemplary use-cases include connecting to an internal knowledge base, retrieving emails from an exchange server, or retrieving order data from a shop backend.

These interactions often require the LLM to authenticate against backend services using API keys specifically created for a technical (Open WebUI) user.

To simplify configuration and secret handling, Open WebUI implements "Valves" and "UserValves" that allow users and administrators to input dynamic details like API keys or configuration options.

Valves have the following distinction:

- **Valves:** Configurable by admins only.
- **UserValves:** Configurable by any user.

The Tool Valves endpoint does not properly restrict read access to the valve. This allows a low privileged user to access all data contained within the valve. In the worst case, this gives a low privileged "Member" user access to sensitive Tool data, such as API keys for third-party systems.

---

# Details

## 1) Broken Access Control in Tool Valves

The following steps can be performed to reproduce the vulnerability.

**1.** An administrator creates an Open WebUI Tool with a configured Valve.

<img width="1038" height="597" alt="image" src="https://github.com/user-attachments/assets/f79bdde9-18fa-49e4-a6c3-5077731f0815" />

**2.** The administrator configures the API key within the Tool Valve.

<img width="1039" height="446" alt="image" src="https://github.com/user-attachments/assets/d88d06b9-fc21-45e5-8142-d9f874601f87" />

**3.** A user with at least "Member" privileges logs into Open WebUI.

The following screenshot shows the user overview of the test instance:

<img width="908" height="354" alt="image" src="https://github.com/user-attachments/assets/40025151-418d-4912-8400-1e1a6e5cd4e4" />

The following screenshot illustrates that the "lowpriv" user doesn't have access to the tool:

<img width="815" height="433" alt="image" src="https://github.com/user-attachments/assets/ec06b07f-9735-4728-9dce-d97d721051b8" />

**4.** The "lowpriv" user uses their Authorization token to retrieve the API key from the Tool Valve.

In order to do so, the attacker needs to know the Tool ID. However, as this ID is always the same for imported tools, and the tool IDs are concatenated from the tool name, guessing tool IDs is trivial.

<img width="754" height="208" alt="image" src="https://github.com/user-attachments/assets/61c80cac-25c8-4730-8156-90869801389f" />

As seen in the following code snippet, the vulnerability is present because the Tool Valves route does not check if the requesting user has administrative permissions (Line 515).

[Source: `backend/open_webui/routers/tools.py` L513–L531](https://github.com/open-webui/open-webui/blob/2b26355002064228e9b671339f8f3fb9d1fafa73/backend/open_webui/routers/tools.py#L513-L531)

---

# PoC

You can find the detailed PoC steps in the [Details](#details) section.

To execute the exploit:

1. Login as a verified user and copy the authorization token.
2. Access the configured valve of any existing tool with the following request (please mind the placeholders):

```http
GET /api/v1/tools/id/<tool_id>/valves HTTP/1.1
Host: <your_test_host>
Authorization: Bearer <authorization_token_from_step_1>
```

---

# Impact

This information disclosure vulnerability allows low privileged users to access sensitive values stored in Tool Valves. Anyone using Open WebUI Tools with a configured Valve is affected. In the worst case, exploitation allows an attacker to access third-party systems within the context of the configured Open WebUI technical user.

---

# Additional Remarks

Additional remarks regarding the CVSS Vector String:

| Component | Value | Rationale |
|-----------|-------|-----------|
| AC | L | Due to the requirement of a "Member" account |
| C | H | Sensitive data, such as API Keys for backend systems, is disclosed |
| S | C | Exploitation of this vulnerability grants access to third-party systems |

---

> **AI report transparency:** AI was used for refinement of this advisory text.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-7429-hxcv-268m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34222
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.11
- http://seclists.org/fulldisclosure/2026/Apr/4
