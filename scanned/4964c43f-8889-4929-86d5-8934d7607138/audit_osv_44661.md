# [C] MOOS essential-moos through 10.0.1 pShare Unauthorized Runtime Route Reconfiguration

## Summary
Severity: Critical
Advisory: CVE-2026-85433
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85433
Type: osv

## Details
MOOS essential-moos pShare through 10.0.1 fails to properly authorize PSHARE_CMD messages, allowing any publisher to reconfigure network routes and listeners at runtime. Attackers can send crafted PSHARE_CMD messages with cmd=output or cmd=input parameters to open new listeners on arbitrary addresses and redirect or duplicate bus traffic to attacker-controlled destinations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85433.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85433
- https://www.vulncheck.com/advisories/moos-essential-moos-through-10.0.1-pshare-unauthorized-runtime-route-reconfiguration
- https://github.com/themoos/essential-moos/commit/8e51cedcbd8de9781adec2e9cce354f51750a547
- https://github.com/themoos/essential-moos/pull/20
- https://github.com/themoos/essential-moos
- https://github.com/themoos/essential-moos/blob/b897ea86dba8b61412dc48ac0cfb5ff34cdaf5f6/Essentials/pShare/Share.cpp#L813
