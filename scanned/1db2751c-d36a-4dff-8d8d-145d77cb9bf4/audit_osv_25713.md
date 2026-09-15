# [H] wazuh-logcollector integer underflow local privilege escalation

## Summary
Severity: High
Advisory: CVE-2023-42463
Aliases: GHSA-27p5-32pp-r58r
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-42463
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. This bug introduced a stack overflow hazard that could allow a local privilege escalation. This vulnerability was patched in version 4.5.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42463.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-27p5-32pp-r58r
- https://nvd.nist.gov/vuln/detail/CVE-2023-42463
