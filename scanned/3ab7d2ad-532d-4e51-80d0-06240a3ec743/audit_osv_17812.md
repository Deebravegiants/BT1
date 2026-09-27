# [M] CVE-2020-2024

## Summary
Severity: Medium
Advisory: CVE-2020-2024
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-2024
Type: osv

## Details
An improper link resolution vulnerability affects Kata Containers versions prior to 1.11.0. Upon container teardown, a malicious guest can trick the kata-runtime into unmounting any mount point on the host and all mount points underneath it, potentiality resulting in a host DoS.

## References
- https://github.com/kata-containers/runtime/issues/2474
- https://github.com/kata-containers/runtime/pull/2475
