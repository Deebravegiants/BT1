# [M] CVE-2021-46916

## Summary
Severity: Medium
Advisory: CVE-2021-46916
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46916
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ixgbe: Fix NULL pointer dereference in ethtool loopback test

The ixgbe driver currently generates a NULL pointer dereference when
performing the ethtool loopback test. This is due to the fact that there
isn't a q_vector associated with the test ring when it is setup as
interrupts are not normally added to the test rings.

To address this I have added code that will check for a q_vector before
returning a napi_id value. If a q_vector is not present it will return a
value of 0.

## References
- https://git.kernel.org/stable/c/31166efb1cee348eb6314e9c0095d84cbeb66b9d
- https://git.kernel.org/stable/c/758d19098df4b0bbca9f40d6ae6c82c9c18b9bba
