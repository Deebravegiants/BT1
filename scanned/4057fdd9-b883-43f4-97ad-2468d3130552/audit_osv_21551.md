# [C] CVE-2021-43845

## Summary
Severity: Critical
Advisory: CVE-2021-43845
Aliases: GHSA-r374-qrwv-86hh
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-12-27
Source: https://osv.dev/vulnerability/CVE-2021-43845
Type: osv

## Details
PJSIP is a free and open source multimedia communication library. In version 2.11.1 and prior, if incoming RTCP XR message contain block, the data field is not checked against the received packet size, potentially resulting in an out-of-bound read access. This affects all users that use PJMEDIA and RTCP XR. A malicious actor can send a RTCP XR message with an invalid packet size.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://security.gentoo.org/glsa/202210-37
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/commit/f74c1fc22b760d2a24369aa72c74c4a9ab985859
- https://github.com/pjsip/pjproject/pull/2924
- https://github.com/pjsip/pjproject/security/advisories/GHSA-r374-qrwv-86hh
