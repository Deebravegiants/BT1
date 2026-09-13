# [H] CVE-2020-29363

## Summary
Severity: High
Advisory: CVE-2020-29363
Aliases: GHSA-5j67-fw89-fp6x
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-16
Source: https://osv.dev/vulnerability/CVE-2020-29363
Type: osv

## Details
An issue was discovered in p11-kit 0.23.6 through 0.23.21. A heap-based buffer overflow has been discovered in the RPC protocol used by p11-kit server/remote commands and the client library. When the remote entity supplies a serialized byte array in a CK_ATTRIBUTE, the receiving entity may not allocate sufficient length for the buffer to store the deserialized value.

## References
- https://github.com/p11-glue/p11-kit/releases
- https://github.com/p11-glue/p11-kit/security/advisories/GHSA-5j67-fw89-fp6x
- https://www.debian.org/security/2021/dsa-4822
- https://www.oracle.com/security-alerts/cpuapr2022.html
