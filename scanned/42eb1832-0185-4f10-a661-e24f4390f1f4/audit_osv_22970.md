# [C] CVE-2022-41837

## Summary
Severity: Critical
Advisory: CVE-2022-41837
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41837
Type: osv

## Details
An out-of-bounds write vulnerability exists in the OpenImageIO::add_exif_item_to_spec functionality of OpenImageIO Project OpenImageIO v2.4.4.2. Specially-crafted exif metadata can lead to stack-based memory corruption. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00005.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1636
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41837.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41837
- https://security.gentoo.org/glsa/202305-33
- https://www.debian.org/security/2023/dsa-5384
