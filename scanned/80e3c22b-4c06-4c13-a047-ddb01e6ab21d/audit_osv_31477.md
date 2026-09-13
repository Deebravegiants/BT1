# [H] evernote-mcp-server openBrowser Command Injection Privilege Escalation Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-12489
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2025-12489
Type: osv

## Details
evernote-mcp-server openBrowser Command Injection Privilege Escalation Vulnerability. This vulnerability allows local attackers to escalate privileges on affected installations of evernote-mcp-server. An attacker must first obtain the ability to execute low-privileged code on the target system in order to exploit this vulnerability.

The specific flaw exists within the openBrowser function. The issue results from the lack of proper validation of a user-supplied string before using it to execute a system call. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the service account. Was ZDI-CAN-27913.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12489.json
- https://github.com/brentmid/evernote-mcp-server/commit/1e66c78c4ce6ea294ac6b0eb289a9eae9c5e9579
- https://nvd.nist.gov/vuln/detail/CVE-2025-12489
- https://www.zerodayinitiative.com/advisories/ZDI-25-983/
