# [H] CVE-2020-21598

## Summary
Severity: High
Advisory: CVE-2020-21598
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-16
Source: https://osv.dev/vulnerability/CVE-2020-21598
Type: osv

## Details
libde265 v1.0.4 contains a heap buffer overflow in the ff_hevc_put_unweighted_pred_8_sse function, which can be exploited via a crafted a file.

## References
- https://cwe.mitre.org/data/definitions/122.html
- https://lists.debian.org/debian-lts-announce/2023/01/msg00020.html
- https://www.debian.org/security/2023/dsa-5346
- https://github.com/strukturag/libde265/issues/237
