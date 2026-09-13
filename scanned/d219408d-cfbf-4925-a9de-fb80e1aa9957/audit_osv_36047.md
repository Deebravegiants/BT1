# [C] CVE-2026-19295

## Summary
Severity: Critical
Advisory: CVE-2026-19295
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-19295
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.11.1 allows an authenticated attacker to execute arbitrary operating system commands in the server process by saving a flow with a crafted type field value and triggering a build of a wrapper flow that references it. This allowed privilege escalation from "authenticated flow user" to arbitrary OS-level command execution under the server process identity, bypassing the LANGFLOW_ALLOW_CUSTOM_COMPONENTS=false policy control.

## References
- https://www.ibm.com/support/pages/node/7284733
