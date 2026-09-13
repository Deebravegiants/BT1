# [C] CVE-2022-41838

## Summary
Severity: Critical
Advisory: CVE-2022-41838
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41838
Type: osv

## Details
A code execution vulnerability exists in the DDS scanline parsing functionality of OpenImageIO Project OpenImageIO v2.4.4.2. A specially-crafted .dds can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1634
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41838.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41838
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
