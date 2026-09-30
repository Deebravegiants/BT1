# [M] CVE-2023-24757

## Summary
Severity: Medium
Advisory: CVE-2023-24757
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-03-01
Source: https://osv.dev/vulnerability/CVE-2023-24757
Type: osv

## Details
libde265 v1.0.10 was discovered to contain a NULL pointer dereference in the put_unweighted_pred_16_fallback function at fallback-motion.cc. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted input file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24757.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-24757
- https://github.com/strukturag/libde265/issues/385
- https://lists.debian.org/debian-lts-announce/2023/03/msg00004.html
