# [H] Suricata dnp3: unbounded transaction growth

## Summary
Severity: High
Advisory: CVE-2026-22259
Aliases: GHSA-878h-2x6v-84q9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-22259
Type: osv

## Details
Suricata is a network IDS, IPS and NSM engine. Prior to versions 8.0.3 and 7.0.14, specially crafted traffic can cause Suricata to consume large amounts of memory while parsing DNP3 traffic. This can lead to the process slowing down and running out of memory, potentially leading to it getting killed by the OOM killer. Versions 8.0.3 or 7.0.14 contain a patch. As a workaround, disable the DNP3 parser in the suricata yaml (disabled by default).

## References
- https://redmine.openinfosecfoundation.org/issues/8181
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22259.json
- https://github.com/OISF/suricata/security/advisories/GHSA-878h-2x6v-84q9
- https://nvd.nist.gov/vuln/detail/CVE-2026-22259
- https://github.com/OISF/suricata/commit/50cac2e2465ca211eabfa156623e585e9037bb7e
- https://github.com/OISF/suricata/commit/63225d5f8ef64cc65164c0bb1800730842d54942
