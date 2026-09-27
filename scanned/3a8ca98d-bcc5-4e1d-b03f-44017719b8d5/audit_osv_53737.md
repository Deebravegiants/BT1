# [M] CVE-2023-2166

## Summary
Severity: Medium
Advisory: CVE-2023-2166
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-2166
Type: osv

## Details
A null pointer dereference issue was found in can protocol in net/can/af_can.c in the Linux before Linux. ml_priv may not be initialized in the receive path of CAN frames. A local user could use this flaw to crash the system or potentially cause a denial of service.

## References
- https://lore.kernel.org/lkml/CAO4mrfcV_07hbj8NUuZrA8FH-kaRsrFy-2metecpTuE5kKHn5w%40mail.gmail.com/
