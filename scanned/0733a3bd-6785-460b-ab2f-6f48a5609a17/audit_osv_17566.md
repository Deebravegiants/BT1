# [M] CVE-2020-16843

## Summary
Severity: Medium
Advisory: CVE-2020-16843
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-04
Source: https://osv.dev/vulnerability/CVE-2020-16843
Type: osv

## Details
In Firecracker 0.20.x before 0.20.1 and 0.21.x before 0.21.2, the network stack can freeze under heavy ingress traffic. This can result in a denial of service on the microVM when it is configured with a single network interface, and an availability problem for the microVM network interface on which the issue is triggered.

## References
- http://www.openwall.com/lists/oss-security/2020/08/13/1
- https://www.openwall.com/lists/oss-security/2020/08/13/1
- https://github.com/firecracker-microvm/firecracker/issues/2057
