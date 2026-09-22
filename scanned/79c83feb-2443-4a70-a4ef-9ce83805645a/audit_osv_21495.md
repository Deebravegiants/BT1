# [H] CVE-2021-43515

## Summary
Severity: High
Advisory: CVE-2021-43515
Aliases: GHSA-64fq-9c6w-rq44
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-04-08
Source: https://osv.dev/vulnerability/CVE-2021-43515
Type: osv

## Details
CSV Injection (aka Excel Macro Injection or Formula Injection) exists in creating new timesheet in Kimai. By filling the Description field with malicious payload, it will be mistreated while exporting to a CSV file.

## References
- https://github.com/kevinpapst/kimai2/commit/dad1b8b772947f1596175add1b4f33b791705507#diff-6774f5865dbaf8bc6c55b75bd92e6f9950ebe7834aa2efd828a19fd637e667cf
