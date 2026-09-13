# [M] CVE-2022-23960

## Summary
Severity: Medium
Advisory: CVE-2022-23960
Aliases: A-215557547, ASB-A-215557547
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-03-13
Source: https://osv.dev/vulnerability/CVE-2022-23960
Type: osv

## Details
Certain Arm Cortex and Neoverse processors through 2022-03-08 do not properly restrict cache speculation, aka Spectre-BHB. An attacker can leverage the shared branch history in the Branch History Buffer (BHB) to influence mispredicted branches. Then, cache allocation can allow the attacker to obtain sensitive information.

## References
- https://developer.arm.com/support/arm-security-updates
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://www.debian.org/security/2022/dsa-5173
- http://www.openwall.com/lists/oss-security/2022/03/18/2
- https://developer.arm.com/support/arm-security-updates/speculative-processor-vulnerability
