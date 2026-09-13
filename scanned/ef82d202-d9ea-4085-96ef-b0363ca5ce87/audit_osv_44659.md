# [M] MOOS essential-moos through 10.0.1 pMOOSBridge Unauthenticated UDP Packet Injection

## Summary
Severity: Medium
Advisory: CVE-2026-85431
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85431
Type: osv

## Details
MOOS essential-moos through version 10.0.1 contains an unauthenticated UDP packet injection vulnerability in pMOOSBridge when configured with UDPListen. Attackers can send crafted UDP packets to the configured port to inject arbitrary variables into the local MOOS community with spoofed source and community identifiers.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85431
- https://www.vulncheck.com/advisories/moos-essential-moos-through-10.0.1-pmoosbridge-unauthenticated-udp-packet-injection
- https://github.com/themoos/essential-moos/commit/d8441eac57d04ee89e7b82723480d10a558b45d6
- https://github.com/themoos/essential-moos/pull/19
- https://github.com/themoos/essential-moos
- https://github.com/themoos/essential-moos/blob/b897ea86dba8b61412dc48ac0cfb5ff34cdaf5f6/Essentials/pMOOSBridge/MOOSUDPLink.cpp#L21
