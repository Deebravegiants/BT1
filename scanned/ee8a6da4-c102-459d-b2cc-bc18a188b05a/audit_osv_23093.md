# [M] CVE-2022-43241

## Summary
Severity: Medium
Advisory: CVE-2022-43241
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/CVE-2022-43241
Type: osv

## Details
Libde265 v1.0.8 was discovered to contain an unknown crash via ff_hevc_put_hevc_qpel_v_3_8_sse in sse-motion.cc. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted video file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43241.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43241
- https://www.debian.org/security/2023/dsa-5346
- https://github.com/strukturag/libde265/issues/338
- https://lists.debian.org/debian-lts-announce/2023/01/msg00020.html
