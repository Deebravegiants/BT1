# [M] CVE-2021-22569

## Summary
Severity: Medium
Advisory: CVE-2021-22569
Aliases: GHSA-wrvw-hg22-4m67
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-22569
Type: osv

## Details
An issue in protobuf-java allowed the interleaving of com.google.protobuf.UnknownFieldSet fields in such a way that would be processed out of order. A small malicious payload can occupy the parser for several minutes by creating large numbers of short-lived objects that cause frequent, repeated pauses. We recommend upgrading libraries beyond the vulnerable versions.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00019.html
- http://www.openwall.com/lists/oss-security/2022/01/12/4
- http://www.openwall.com/lists/oss-security/2022/01/12/7
- https://cloud.google.com/support/bulletins#gcp-2022-001
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=39330
- https://www.oracle.com/security-alerts/cpuapr2022.html
