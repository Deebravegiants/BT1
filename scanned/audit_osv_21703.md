# [H] CVE-2021-45773

## Summary
Severity: High
Advisory: CVE-2021-45773
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-45773
Type: osv

## Details
A NULL pointer dereference in CS104_IPAddress_setFromString at src/iec60870/cs104/cs104_slave.c of lib60870 commit 0d5e76e can lead to a segmentation fault or application crash.

## References
- https://github.com/mz-automation/lib60870/issues/100
