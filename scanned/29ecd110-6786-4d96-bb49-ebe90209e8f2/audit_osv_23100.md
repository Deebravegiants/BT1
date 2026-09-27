# [M] CVE-2022-43250

## Summary
Severity: Medium
Advisory: CVE-2022-43250
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/CVE-2022-43250
Type: osv

## Details
Libde265 v1.0.8 was discovered to contain a heap-buffer-overflow vulnerability via put_qpel_0_0_fallback_16 in fallback-motion.cc. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted video file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43250.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43250
- https://www.debian.org/security/2023/dsa-5346
- https://github.com/strukturag/libde265/issues/346
- https://lists.debian.org/debian-lts-announce/2023/01/msg00020.html
