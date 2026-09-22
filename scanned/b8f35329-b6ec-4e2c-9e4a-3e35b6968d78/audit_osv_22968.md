# [C] CVE-2022-41794

## Summary
Severity: Critical
Advisory: CVE-2022-41794
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41794
Type: osv

## Details
A heap based buffer overflow vulnerability exists in the PSD thumbnail resource parsing code of OpenImageIO 2.3.19.0. A specially-crafted PSD file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00005.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1626
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41794.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41794
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
