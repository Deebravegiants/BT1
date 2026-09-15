# [H] CVE-2022-41649

## Summary
Severity: High
Advisory: CVE-2022-41649
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41649
Type: osv

## Details
A heap out of bounds read vulnerability exists in the handling of IPTC data while parsing TIFF images in OpenImageIO v2.3.19.0. A specially-crafted TIFF file can cause a read of adjacent heap memory, which can leak sensitive process information. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00005.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1631
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41649.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41649
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
