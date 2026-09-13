# [H] CVE-2021-36409

## Summary
Severity: High
Advisory: CVE-2021-36409
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-36409
Type: osv

## Details
There is an Assertion `scaling_list_pred_matrix_id_delta==1' failed at sps.cc:925 in libde265 v1.0.8 when decoding file, which allows attackers to cause a Denial of Service (DoS) by running the application with a crafted file or possibly have unspecified other impact.

## References
- https://github.com/strukturag/libde265/issues/300
- https://lists.debian.org/debian-lts-announce/2022/12/msg00027.html
- https://www.debian.org/security/2023/dsa-5346
