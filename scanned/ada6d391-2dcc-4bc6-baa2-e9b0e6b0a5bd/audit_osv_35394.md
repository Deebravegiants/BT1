# [H] picklescan - Remote Code Execution via idlelib.debugobj.ObjectTreeItem.SetText

## Summary
Severity: High
Advisory: CVE-2025-71354
Aliases: GHSA-3vg9-h568-4w9m, PYSEC-2026-1781
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-71354
Type: osv

## Details
picklescan before 0.0.29 fails to detect malicious pickle files that exploit idlelib.debugobj.ObjectTreeItem.SetText function in reduce methods. Attackers can craft pickle files with embedded code that bypasses picklescan detection and executes arbitrary commands when pickle.load() is called.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71354.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-3vg9-h568-4w9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-71354
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-idlelib-debugobj-objecttreeitem-settext
