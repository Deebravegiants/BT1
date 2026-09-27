# [M] CVE-2021-47164

## Summary
Severity: Medium
Advisory: CVE-2021-47164
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47164
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix null deref accessing lag dev

It could be the lag dev is null so stop processing the event.
In bond_enslave() the active/backup slave being set before setting the
upper dev so first event is without an upper dev.
After setting the upper dev with bond_master_upper_dev_link() there is
a second event and in that event we have an upper dev.

## References
- https://git.kernel.org/stable/c/2e4b0b95a489259f9d35a3db17023061f8f3d587
- https://git.kernel.org/stable/c/83026d83186bc48bb41ee4872f339b83f31dfc55
- https://git.kernel.org/stable/c/bdfd3593a8248eea6ecfcbf7b47b56b86515672d
