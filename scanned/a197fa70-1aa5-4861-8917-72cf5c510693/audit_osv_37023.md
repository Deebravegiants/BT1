# [M] EVerest: ISO15118 session_setup use-after-free can crash EVSE process

## Summary
Severity: Medium
Advisory: CVE-2026-27828
Aliases: GHSA-5g3v-qc79-qqwr
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-27828
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, ISO15118_chargerImpl::handle_session_setup uses v2g_ctx after it has been freed when ISO15118 initialization fails (e.g., no IPv6 link-local address). The EVSE process can be crashed remotely by an attacker with MQTT access who issues a session_setup command while v2g_ctx has been released. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27828.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-5g3v-qc79-qqwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27828
