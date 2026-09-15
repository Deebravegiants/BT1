# [C] CVE-2026-10134

## Summary
Severity: Critical
Advisory: CVE-2026-10134
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-10134
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.9.3 allows an attacker to read every secret available to the Langflow process, read and modify every flow, conversation, message, file upload, and saved component in the Langflow database, can connect to internal services, abuse cloud metadata endpoints, laterally move to other tenants on the same Langflow instance, and Establish persistence by modifying the public flow's `tool_code` so normal `/api/v1/build/...` calls by any user re-execute attacker code at each build.

## References
- https://www.ibm.com/support/pages/node/7277559
