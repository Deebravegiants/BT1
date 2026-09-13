# [H] Dataease arbitrary interface access vulnerability

## Summary
Severity: High
Advisory: CVE-2024-47073
Aliases: GHSA-5jr4-wrm2-xj36
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-47073
Type: osv

## Details
DataEase is an open source data visualization analysis tool that helps users quickly analyze data and gain insights into business trends. In affected versions a the lack of signature verification of jwt tokens allows attackers to forge jwts which then allow access to any interface. The vulnerability has been fixed in v2.10.2 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47073.json
- https://github.com/dataease/dataease/security/advisories/GHSA-5jr4-wrm2-xj36
- https://nvd.nist.gov/vuln/detail/CVE-2024-47073
