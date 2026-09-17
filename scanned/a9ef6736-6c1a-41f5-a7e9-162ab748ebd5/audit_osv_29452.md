# [M] A malformed Contact or Record-Route URI in an incoming SIP request can cause Asterisk to crash when res_resolver_unbound is used

## Summary
Severity: Medium
Advisory: CVE-2024-42491
Aliases: GHSA-v428-g3cw-7hv9
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/CVE-2024-42491
Type: osv

## Details
Asterisk is an open-source private branch exchange (PBX). Prior to versions 18.24.3, 20.9.3, and 21.4.3 of Asterisk and versions 18.9-cert12 and 20.7-cert2 of certified-asterisk, if Asterisk attempts to send a SIP request to a URI whose host portion starts with `.1` or `[.1]`, and res_resolver_unbound is loaded, Asterisk will crash with a SEGV. To receive a patch, users should upgrade to one of the following versions: 18.24.3, 20.9.3, 21.4.3, certified-18.9-cert12, certified-20.7-cert2. Two workarounds are available. Disable res_resolver_unbound by setting `noload = res_resolver_unbound.so` in modules.conf, or set `rewrite_contact = yes` on all PJSIP endpoints. NOTE: This may not be appropriate for all Asterisk configurations.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42491.json
- https://github.com/asterisk/asterisk/security/advisories/GHSA-v428-g3cw-7hv9
- https://nvd.nist.gov/vuln/detail/CVE-2024-42491
- https://github.com/asterisk/asterisk/commit/42a2f4ccfa2c7062a15063e765916b3332e34cc4
- https://github.com/asterisk/asterisk/commit/4f01669c7c41c9184f3cce9a3cf1b2ebf6201742
- https://github.com/asterisk/asterisk/commit/50bf8d4d3064930d28ecf1ce3397b14574d514d2
- https://github.com/asterisk/asterisk/commit/7a0090325bfa9d778a39ae5f7d0a98109e4651c8
- https://github.com/asterisk/asterisk/commit/a15050650abf09c10a3c135fab148220cd41d3a0
