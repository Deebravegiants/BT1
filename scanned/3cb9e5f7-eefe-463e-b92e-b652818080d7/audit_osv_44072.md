# [H] Incorrect Permission Assignment for Critical Resource in Elastic Agent Leading to Local Privilege Escalation to SYSTEM

## Summary
Severity: High
Advisory: CVE-2026-78604
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78604
Type: osv

## Details
Incorrect Permission Assignment for Critical Resource (CWE-732) in Elastic Agent can lead to local privilege escalation via Replace Binaries (CAPEC-642). On Windows systems where Elastic Agent is installed in unprivileged mode, resources used by the agent service are created with access controls broader than required. A local user could take advantage of this to cause the service to execute code of their choosing, ultimately obtaining SYSTEM-level privileges on the host.

## References
- https://discuss.elastic.co/t/elastic-agent-8-19-21-9-4-6-9-5-2-security-update-esa-2026-150/390109
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78604.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78604
