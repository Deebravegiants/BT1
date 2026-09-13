# [H] CVE-2026-9201

## Summary
Severity: High
Advisory: CVE-2026-9201
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-9201
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3 could allow an authenticated attacker to execute arbitrary code due to a cryptographic weakness in the custom component validation mechanism. When the optional hardening mode that restricts execution to trusted component templates is enabled, the application validates component code using a truncated SHA‑256 hash. Because the hash comparison relies on only a portion of the digest, an attacker can craft malicious component code that collides with a trusted template hash and bypasses validation. Successful exploitation allows the attacker to introduce and execute unauthorized Python code within the Langflow process, defeating the intended security control and potentially leading to full compromise of the affected instance.

## References
- https://www.ibm.com/support/pages/node/7282646
