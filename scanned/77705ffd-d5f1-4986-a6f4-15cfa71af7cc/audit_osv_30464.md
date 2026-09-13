# [M] Elastic Agent Inclusion of Functionality from Untrusted Control Sphere

## Summary
Severity: Medium
Advisory: CVE-2024-52976
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2024-52976
Type: osv

## Details
Inclusion of functionality from an untrusted control sphere in Elastic Agent subprocess, osqueryd, allows local attackers to execute arbitrary code via parameter injection.

An attacker requires local access and the ability to modify osqueryd configurations.

## References
- https://discuss.elastic.co/t/elastic-agent-7-17-25-and-8-15-4-security-update-esa-2024-39/377708
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52976.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52976
