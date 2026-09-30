# [M] CVE-2021-24119

## Summary
Severity: Medium
Advisory: CVE-2021-24119
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-14
Source: https://osv.dev/vulnerability/CVE-2021-24119
Type: osv

## Details
In Trusted Firmware Mbed TLS 2.24.0, a side-channel vulnerability in base64 PEM file decoding allows system-level (administrator) attackers to obtain information about secret RSA keys via a controlled-channel and side-channel attack on software running in isolated environments that can be single stepped, especially Intel SGX.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00034.html
- https://github.com/ARMmbed/mbedtls/releases
- https://github.com/UzL-ITS/util-lookup/blob/main/cve-vulnerability-publication.md
- https://lists.debian.org/debian-lts-announce/2021/11/msg00021.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DRRVY7DMTX3ECFNZKDYTSFEG5AI2HBC6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EYJW7HAW3TDV2YMDFYXP3HD6WRQRTLJW/
