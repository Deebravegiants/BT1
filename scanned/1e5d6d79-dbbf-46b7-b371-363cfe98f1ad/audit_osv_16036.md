# [M] CVE-2019-25076

## Summary
Severity: Medium
Advisory: CVE-2019-25076
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2022-09-08
Source: https://osv.dev/vulnerability/CVE-2019-25076
Type: osv

## Details
The TSS (Tuple Space Search) algorithm in Open vSwitch 2.x through 2.17.2 and 3.0.0 allows remote attackers to cause a denial of service (delays of legitimate traffic) via crafted packet data that requires excessive evaluation time within the packet classification algorithm for the MegaFlow cache, aka a Tuple Space Explosion (TSE) attack.

## References
- https://arxiv.org/abs/2011.09107
- https://dl.acm.org/citation.cfm?doid=3359989.3365431
- https://sites.google.com/view/tuple-space-explosion
- https://www.youtube.com/watch?v=5cHpzVK0D28
- https://www.youtube.com/watch?v=DSC3m-Bww64
