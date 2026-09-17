# [H] CVE-2018-19499

## Summary
Severity: High
Advisory: CVE-2018-19499
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-23
Source: https://osv.dev/vulnerability/CVE-2018-19499
Type: osv

## Details
Vanilla before 2.5.5 and 2.6.x before 2.6.2 allows Remote Code Execution because authenticated administrators have a reachable call to unserialize in the Gdn_Format class.

## References
- https://hackerone.com/reports/407552
