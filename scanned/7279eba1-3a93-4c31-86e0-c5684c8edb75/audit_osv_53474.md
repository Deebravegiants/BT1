# [M] CVE-2022-44641

## Summary
Severity: Medium
Advisory: CVE-2022-44641
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/CVE-2022-44641
Type: osv

## Details
In Linaro Automated Validation Architecture (LAVA) before 2022.11, users with valid credentials can submit crafted XMLRPC requests that cause a recursive XML entity expansion, leading to excessive use of memory on the server and a Denial of Service.

## References
- https://lists.lavasoftware.org/archives/list/lava-announce%40lists.lavasoftware.org/thread/WHXGQMIZAPW3GCQEXYHC32N2ZAAAIYCY/
- https://lists.debian.org/debian-lts-announce/2023/01/msg00016.html
- https://www.debian.org/security/2023/dsa-5318
