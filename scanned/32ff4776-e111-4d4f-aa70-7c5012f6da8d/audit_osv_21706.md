# [C] CVE-2021-45790

## Summary
Severity: Critical
Advisory: CVE-2021-45790
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2021-45790
Type: osv

## Details
An arbitrary file upload vulnerability was found in Metersphere v1.15.4. Unauthenticated users can upload any file to arbitrary directory, where attackers can write a cron job to execute commands.

## References
- https://github.com/metersphere/metersphere/issues/8653
