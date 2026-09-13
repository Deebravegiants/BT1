# [M] CVE-2022-43592

## Summary
Severity: Medium
Advisory: CVE-2022-43592
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-43592
Type: osv

## Details
An information disclosure vulnerability exists in the DPXOutput::close() functionality of OpenImageIO Project OpenImageIO v2.4.4.2. A specially crafted ImageOutput Object can lead to leaked heap data. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1651
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43592.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43592
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
