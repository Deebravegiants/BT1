# [H] CVE-2020-27151

## Summary
Severity: High
Advisory: CVE-2020-27151
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-07
Source: https://osv.dev/vulnerability/CVE-2020-27151
Type: osv

## Details
An issue was discovered in Kata Containers through 1.11.3 and 2.x through 2.0-rc1. The runtime will execute binaries given using annotations without any kind of validation. Someone who is granted access rights to a cluster will be able to have kata-runtime execute arbitrary binaries as root on the worker nodes.

## References
- https://github.com/kata-containers/kata-containers/releases/tag/2.0.0
- https://github.com/kata-containers/runtime/releases/tag/1.11.5
- https://github.com/kata-containers/runtime/releases/tag/1.12.0
- https://bugs.launchpad.net/katacontainers.io/+bug/1878234
