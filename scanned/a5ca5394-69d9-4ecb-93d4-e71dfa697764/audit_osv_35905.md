# [M] Privilege Escalation in Eclipse hawkBit DDI allows Tenant-Isolated Firmware Exfiltration

## Summary
Severity: Medium
Advisory: CVE-2026-16454
Aliases: GHSA-92r3-p8c2-3fpx
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-16454
Type: osv

## Details
In Eclipse hawkBit versions 1.0.3 and prior, a privilege escalation vulnerability (CWE-284 / CWE-862) has been identified in the Direct Device Integration (DDI) Controller.



This vulnerability allows an authenticated device to escalate its permissions and bypass the strict boundaries of its assigned updates. Under normal operation, a device should be restricted strictly to the specific firmware artifacts explicitly assigned to it. However, this flaw enables any authenticated device to bypass this restriction and download any firmware artifact within the same tenant.



This is not an authentication bypass; the requesting device must possess valid credentials for its respective tenant. Instead, the issue stems from a flaw in object-level authorization validation.



A related, lower-severity helper issue exists in the listing software modules artifacts metadata endpoint. This endpoint does not enforce assignment checks, enabling an authenticated device to list and enumerate available firmware artifacts, which can facilitate targeted exfiltration using the main download authorization bypass.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/196
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16454.json
- https://github.com/eclipse-hawkbit/hawkbit/security/advisories/GHSA-92r3-p8c2-3fpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-16454
