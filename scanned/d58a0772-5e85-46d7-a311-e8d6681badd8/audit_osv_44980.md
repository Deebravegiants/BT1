# [H] CVE-2026-9196

## Summary
Severity: High
Advisory: CVE-2026-9196
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-9196
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 could allow an authenticated attacker to execute unintended code during Agentic Assistant validation due to improper handling of LLM‑generated components. The application executes model‑generated Python code in the backend during validation prior to user approval, which may allow an attacker to trigger side effects such as outbound network access, file system interaction, or data exfiltration with the privileges of the Langflow backend process.

## References
- https://www.ibm.com/support/pages/node/7282646
