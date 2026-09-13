# [M] CVE-2022-3903

## Summary
Severity: Medium
Advisory: CVE-2022-3903
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-14
Source: https://osv.dev/vulnerability/CVE-2022-3903
Type: osv

## Details
An incorrect read request flaw was found in the Infrared Transceiver USB driver in the Linux kernel. This issue occurs when a user attaches a malicious USB device. A local user could use this flaw to starve the resources, causing denial of service or potentially crashing the system.

## References
- https://lore.kernel.org/all/CAB7eexLLApHJwZfMQ=X-PtRhw0BgO+5KcSMS05FNUYejJXqtSA%40mail.gmail.com/
- https://lore.kernel.org/all/E1obysd-009Grw-He%40www.linuxtv.org/
