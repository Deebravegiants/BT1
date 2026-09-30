# [M] CVE-2024-24859

## Summary
Severity: Medium
Advisory: CVE-2024-24859
CVSS: 4.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-02-05
Source: https://osv.dev/vulnerability/CVE-2024-24859
Type: osv

## Details
A race condition was found in the Linux kernel's net/bluetooth in sniff_{min,max}_interval_set() function. This can result in a bluetooth sniffing exception issue, possibly leading denial of service.

## References
- https://bugzilla.openanolis.cn/show_bug.cgi?id=8153
