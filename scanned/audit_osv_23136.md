# [M] CVE-2022-43596

## Summary
Severity: Medium
Advisory: CVE-2022-43596
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-43596
Type: osv

## Details
An information disclosure vulnerability exists in the IFFOutput channel interleaving functionality of OpenImageIO Project OpenImageIO v2.4.4.2. A specially crafted ImageOutput Object can lead to leaked heap data. An attacker can provide malicious input to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1654
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43596.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43596
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
