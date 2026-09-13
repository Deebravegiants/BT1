# [M] CVE-2022-41684

## Summary
Severity: Medium
Advisory: CVE-2022-41684
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-41684
Type: osv

## Details
A heap out of bounds read vulnerability exists in the OpenImageIO master-branch-9aeece7a when parsing the image file directory part of a PSD image file. A specially-crafted .psd file can cause a read of arbitrary memory address which can lead to denial of service. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00005.html
- https://www.debian.org/security/2023/dsa-5384
- https://security.gentoo.org/glsa/202305-33
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1632
