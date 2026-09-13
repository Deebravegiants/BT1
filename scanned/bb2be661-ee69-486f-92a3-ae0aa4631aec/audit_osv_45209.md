# [M] Arm Mbed TLS before 2.16.5 allows attackers to obtain sensitive information (an RSA private key) by...

## Summary
Severity: Medium
Advisory: JLSEC-2025-200
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/JLSEC-2025-200
Type: osv

## Affected
- Julia: `MbedTLS_jll` — affected >=0 <2.16.6+0

## Details
Arm Mbed TLS before 2.16.5 allows attackers to obtain sensitive information (an RSA private key) by measuring cache usage during an import.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5JPE2HFBDJF3UBT6Q4VWLKNKCVCMX25J/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WD6OSOLLAR2AVPJAMGUKWRXN6477IHHV/
- https://tls.mbed.org/tech-updates/security-advisories/mbedtls-security-advisory-2020-02
