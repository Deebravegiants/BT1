# [H] CVE-2021-21772

## Summary
Severity: High
Advisory: CVE-2021-21772
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2021-21772
Type: osv

## Details
A use-after-free vulnerability exists in the NMR::COpcPackageReader::releaseZIP() functionality of 3MF Consortium lib3mf 2.0.0. A specially crafted 3MF file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IHMMHD2EOMIVJ7EKZTJJMX4C7E6ZRWDL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NPBS642OYVA6DUKK3HZHEINVWEDZSMEU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WDGGB65YBQL662M3MOBNNJJNRNURW4TG/
- https://security.gentoo.org/glsa/202208-01
- https://www.debian.org/security/2021/dsa-4887
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1226
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2021-1226
