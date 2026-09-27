# [C] CVE-2016-10721

## Summary
Severity: Critical
Advisory: CVE-2016-10721
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2016-10721
Type: osv

## Details
partclone.restore in Partclone 0.2.87 is prone to a heap-based buffer overflow vulnerability due to insufficient validation of the partclone image header. An attacker may be able to execute arbitrary code in the context of the user running the affected application.

## References
- https://github.com/Thomas-Tsai/partclone/issues/82
