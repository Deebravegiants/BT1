# [H] MOOS essential-moos through 10.0.1 pShare Unauthenticated UDP Datagram Republishing

## Summary
Severity: High
Advisory: CVE-2026-85430
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85430
Type: osv

## Details
MOOS essential-moos through 10.0.1 contains an authentication bypass vulnerability in pShare that accepts UDP datagrams from any source and republishes them with the attacker-claimed identity intact. Attackers can send crafted UDP datagrams to pShare input routes to inject messages into the local MOOS community under spoofed identities, or send malformed datagrams to crash the pShare process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85430.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85430
- https://www.vulncheck.com/advisories/moos-essential-moos-through-10.0.1-pshare-unauthenticated-udp-datagram-republishing
- https://github.com/themoos/essential-moos/commit/53729b6325a991a8dbd84dcd04e4707f3e592fd6
- https://github.com/themoos/essential-moos/pull/18
- https://github.com/themoos/essential-moos
- https://github.com/themoos/essential-moos/blob/b897ea86dba8b61412dc48ac0cfb5ff34cdaf5f6/Essentials/pShare/Listener.cpp#L132
