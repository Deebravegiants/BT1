# [C] CVE-2022-41639

## Summary
Severity: Critical
Advisory: CVE-2022-41639
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41639
Type: osv

## Details
A heap based buffer overflow vulnerability exists in tile decoding code of TIFF image parser in OpenImageIO master-branch-9aeece7a and v2.3.19.0. A specially-crafted TIFF file can lead to an out of bounds memory corruption, which can result in arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1633
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41639.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41639
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
