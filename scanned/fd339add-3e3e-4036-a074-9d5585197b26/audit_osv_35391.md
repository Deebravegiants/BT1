# [H] picklescan - Remote Code Execution via timeit.timeit() Detection Bypass

## Summary
Severity: High
Advisory: CVE-2025-71351
Aliases: GHSA-v7x6-rv5q-mhwc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2025-71351
Type: osv

## Details
picklescan before 0.0.25 fails to detect malicious pickle files that use timeit.timeit() in the __reduce__ method, allowing remote code execution. Attackers can craft pickle files that import dangerous libraries like os and execute arbitrary system commands, which evade picklescan detection and execute when pickle.load() is called.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71351.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-v7x6-rv5q-mhwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-71351
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-timeit-timeit-detection-bypass
