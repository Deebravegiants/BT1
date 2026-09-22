# [C] CVE-2021-27213

## Summary
Severity: Critical
Advisory: CVE-2021-27213
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-14
Source: https://osv.dev/vulnerability/CVE-2021-27213
Type: osv

## Details
config.py in pystemon before 2021-02-13 allows code execution via YAML deserialization because SafeLoader and safe_load are not used.

## References
- https://github.com/cvandeplas/pystemon/commit/dbeb87afefdb63de2f4cff69b6f10c5965d14b54
- https://www.huntr.dev/bounties/1-other-pystemon/
