# [M] CVE-2022-43594

## Summary
Severity: Medium
Advisory: CVE-2022-43594
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-43594
Type: osv

## Details
Multiple denial of service vulnerabilities exist in the image output closing functionality of OpenImageIO Project OpenImageIO v2.4.4.2. Specially crafted ImageOutput Objects can lead to multiple null pointer dereferences. An attacker can provide malicious multiple inputs to trigger these vulnerabilities.This vulnerability applies to writing .bmp files.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1653
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43594.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43594
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
