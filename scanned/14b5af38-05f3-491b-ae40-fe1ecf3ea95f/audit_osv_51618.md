# [H] CVE-2021-3600

## Summary
Severity: High
Advisory: CVE-2021-3600
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-08
Source: https://osv.dev/vulnerability/CVE-2021-3600
Type: osv

## Details
It was discovered that the eBPF implementation in the Linux kernel did not properly track bounds information for 32 bit registers when performing div and mod operations. A local attacker could use this to possibly execute arbitrary code.

## References
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-3600
- https://ubuntu.com/security/notices/USN-5003-1
- https://git.kernel.org/linus/e88b2c6e5a4d9ce30d75391e4d950da74bb2bd90
