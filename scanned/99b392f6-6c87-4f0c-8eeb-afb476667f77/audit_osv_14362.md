# [M] CVE-2018-9481

## Summary
Severity: Medium
Advisory: CVE-2018-9481
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-20
Source: https://osv.dev/vulnerability/CVE-2018-9481
Type: osv

## Details
In bta_hd_set_report_act of bta_hd_act.cc, there is a possible out-of-bounds read due to an integer overflow. This could lead to remote information disclosure in the Bluetooth service with no additional execution privileges needed. User interaction is not needed for exploitation.

## References
- https://lists.apache.org/thread.html/rcb8bae0b289d71d18a3220be256c1dfcc4d9ab49d2d6e07d1eac7c9d@%3Cdev.trafficserver.apache.org%3E
