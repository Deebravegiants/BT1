# [H] CVE-2022-43599

## Summary
Severity: High
Advisory: CVE-2022-43599
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-43599
Type: osv

## Details
Multiple code execution vulnerabilities exist in the IFFOutput::close() functionality of OpenImageIO Project OpenImageIO v2.4.4.2. A specially crafted ImageOutput Object can lead to a heap buffer overflow. An attacker can provide malicious input to trigger these vulnerabilities.This vulnerability arises when the `xmax` variable is set to 0xFFFF and `m_spec.format` is `TypeDesc::UINT8`

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1656
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43599.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43599
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
