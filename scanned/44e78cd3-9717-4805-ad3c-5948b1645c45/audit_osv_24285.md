# [C] ProtonVPN 1.26.0 - Unquoted Service Path

## Summary
Severity: Critical
Advisory: CVE-2022-50917
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2022-50917
Type: osv

## Details
ProtonVPN 1.26.0 contains an unquoted service path vulnerability in its WireGuard service configuration that allows local attackers to potentially execute arbitrary code. Attackers can exploit the unquoted path by placing malicious executables in specific file system locations to gain elevated privileges during service startup.

## References
- https://protonvpn.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50917.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50917
- https://www.vulncheck.com/advisories/protonvpn-unquoted-service-path
- https://www.exploit-db.com/exploits/50837
