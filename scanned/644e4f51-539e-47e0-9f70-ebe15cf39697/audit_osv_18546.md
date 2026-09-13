# [H] CVE-2020-28599

## Summary
Severity: High
Advisory: CVE-2020-28599
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-24
Source: https://osv.dev/vulnerability/CVE-2020-28599
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the import_stl.cc:import_stl() functionality of Openscad openscad-2020.12-RC2. A specially crafted STL file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AFXQZK6BAYARVVWBBXDKPVPN3N77PPDX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KRHYUWXQ7QQIC6TXDYYLYFFF7B7L3EBD/
- https://security.gentoo.org/glsa/202107-35
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1223
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2020-1224
