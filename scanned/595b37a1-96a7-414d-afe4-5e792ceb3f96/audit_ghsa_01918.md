# [C] Path traversal in impacket

## Summary
Severity: Critical
Advisory: GHSA-mj63-64x7-57xf
CVE: CVE-2021-31800
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-mj63-64x7-57xf
Type: github-advisory

## Affected
- PyPI: `impacket` — affected >=0 <0.9.23

## Details
Multiple path traversal vulnerabilities exist in smbserver.py in Impacket before 0.9.23. An attacker that connects to a running smbserver instance can list and write to arbitrary files via ../ directory traversal. This could potentially be abused to achieve arbitrary code execution by replacing /etc/shadow or an SSH authorized key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31800
- https://github.com/SecureAuthCorp/impacket/commit/49c643bf66620646884ed141c94e5fdd85bcdd2f
- https://github.com/SecureAuthCorp/impacket/commit/99bd29e3995c254e2d6f6c2e3454e4271665955a
- https://github.com/SecureAuthCorp/impacket/blob/cb6d43a677c338db930bc4e9161620832c1ec624/impacket/smbserver.py#L2008
- https://github.com/SecureAuthCorp/impacket/blob/cb6d43a677c338db930bc4e9161620832c1ec624/impacket/smbserver.py#L2958
- https://github.com/SecureAuthCorp/impacket/blob/cb6d43a677c338db930bc4e9161620832c1ec624/impacket/smbserver.py#L3485
- https://github.com/SecureAuthCorp/impacket/blob/cb6d43a677c338db930bc4e9161620832c1ec624/impacket/smbserver.py#L876
- https://github.com/SecureAuthCorp/impacket/releases
- https://github.com/SecureAuthCorp/impacket/releases/tag/impacket_0_9_23
- https://github.com/advisories/GHSA-mj63-64x7-57xf
- https://github.com/fortra/impacket
- https://github.com/pypa/advisory-database/tree/main/vulns/impacket/PYSEC-2021-17.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPXDPWCAPVX3UWYZ3N2T5OLBSBBUHJP6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KRV2C5DATXBHG6TF6CEEX54KZ75THQS3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UF56LYB27LHEIFJTFHU3M75NMNNK2SCG
