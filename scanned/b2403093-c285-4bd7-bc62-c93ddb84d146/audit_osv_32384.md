# [H] CVE-2025-29311

## Summary
Severity: High
Advisory: CVE-2025-29311
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-24
Source: https://osv.dev/vulnerability/CVE-2025-29311
Type: osv

## Details
Limited secret space in LLDP packets used in onos v2.7.0 allows attackers to obtain the private key via a bruteforce attack. Attackers are able to leverage this vulnerability into creating crafted LLDP packets.

## References
- https://gist.github.com/Saber-Berserker/790f2a75ae482df3fd0fce569f30504a;
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29311.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29311
