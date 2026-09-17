# [H] CVE-2021-26567

## Summary
Severity: High
Advisory: CVE-2021-26567
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-26567
Type: osv

## Details
Stack-based buffer overflow vulnerability in frontend/main.c in faad2 before 2.2.7.1 allow local attackers to execute arbitrary code via filename and pathname options.

## References
- https://www.synology.com/security/advisory/Synology_SA_20_26
- https://github.com/knik0/faad2/commit/720f7004d6c4aabee19aad16e7c456ed76a3ebfa
