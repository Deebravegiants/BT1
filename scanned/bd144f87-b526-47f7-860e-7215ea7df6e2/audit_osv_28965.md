# [H] Suricata modbus: txs without responses are never freed

## Summary
Severity: High
Advisory: CVE-2024-38534
Aliases: GHSA-59qg-h357-69fq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-38534
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Crafted modbus traffic can lead to unlimited resource accumulation within a flow. Upgrade to 7.0.6. Set a limited stream.reassembly.depth to reduce the issue.

## References
- https://redmine.openinfosecfoundation.org/issues/6987
- https://redmine.openinfosecfoundation.org/issues/6988
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38534.json
- https://github.com/OISF/suricata/security/advisories/GHSA-59qg-h357-69fq
- https://nvd.nist.gov/vuln/detail/CVE-2024-38534
- https://github.com/OISF/suricata/commit/a753cdbe84caee3b66d0bf49b2712d29a50d67ae
