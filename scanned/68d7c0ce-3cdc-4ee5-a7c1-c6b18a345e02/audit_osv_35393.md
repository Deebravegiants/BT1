# [H] picklescan - Remote Code Execution via torch._dynamo.guards.GuardBuilder.get

## Summary
Severity: High
Advisory: CVE-2025-71353
Aliases: GHSA-86cj-95qr-2p4f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71353
Type: osv

## Details
picklescan before 0.0.28 fails to detect malicious pickle files that exploit torch._dynamo.guards.GuardBuilder.get function in reduce methods. Attackers can craft pickle files with embedded code that evades picklescan detection and executes arbitrary commands when loaded.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71353.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-86cj-95qr-2p4f
- https://nvd.nist.gov/vuln/detail/CVE-2025-71353
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-torch-dynamo-guards-guardbuilder-get
