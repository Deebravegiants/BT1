# [H] CVE-2026-26514

## Summary
Severity: High
Advisory: CVE-2026-26514
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-26514
Type: osv

## Details
An Argument Injection vulnerability exists in bird-lg-go before commit 6187a4e. The traceroute module uses shlex.Split to parse user input without validation, allowing remote attackers to inject arbitrary flags (e.g., -w, -q) via the q parameter. This can be exploited to cause a Denial of Service (DoS) by exhausting system resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26514.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26514
- https://github.com/xddxdd/bird-lg-go/issues/136
- https://github.com/xddxdd/bird-lg-go/commit/6187a4e3afce6d8c29568f8c72ca497d1f5a2b56
