# [M] CVE-2020-28588

## Summary
Severity: Medium
Advisory: CVE-2020-28588
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-10
Source: https://osv.dev/vulnerability/CVE-2020-28588
Type: osv

## Details
An information disclosure vulnerability exists in the /proc/pid/syscall functionality of Linux Kernel 5.1 Stable and 5.4.66. More specifically, this issue has been introduced in v5.1-rc4 (commit 631b7abacd02b88f4b0795c08b54ad4fc3e7c7c0) and is still present in v5.10-rc4, so it’s likely that all versions in between are affected. An attacker can read /proc/pid/syscall to trigger this vulnerability, which leads to the kernel leaking memory contents.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1211
