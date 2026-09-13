# [H] Suricata detect/datasets: reachable assertion with unimplemented rule option

## Summary
Severity: High
Advisory: CVE-2024-45795
Aliases: GHSA-6r8w-fpw6-cp9g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-45795
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to version 7.0.7, rules using datasets with the non-functional / unimplemented "unset" option can trigger an assertion during traffic parsing, leading to denial of service. This issue is addressed in 7.0.7. As a workaround, use only trusted and well tested rulesets.

## References
- https://redmine.openinfosecfoundation.org/issues/7195
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45795.json
- https://github.com/OISF/suricata/security/advisories/GHSA-6r8w-fpw6-cp9g
- https://nvd.nist.gov/vuln/detail/CVE-2024-45795
