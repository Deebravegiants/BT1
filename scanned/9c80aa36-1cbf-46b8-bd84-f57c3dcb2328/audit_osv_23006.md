# [M] CVE-2022-41977

## Summary
Severity: Medium
Advisory: CVE-2022-41977
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41977
Type: osv

## Details
An out of bounds read vulnerability exists in the way OpenImageIO version v2.3.19.0 processes string fields in TIFF image files. A specially-crafted TIFF file can lead to information disclosure. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1627
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41977.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41977
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
