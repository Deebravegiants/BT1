# [M] CVE-2021-3543

## Summary
Severity: Medium
Advisory: CVE-2021-3543
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-3543
Type: osv

## Details
A flaw null pointer dereference in the Nitro Enclaves kernel driver was found in the way that Enclaves VMs forces closures on the enclave file descriptor. A local user of a host machine could use this flaw to crash the system or escalate their privileges on the system.

## References
- https://lore.kernel.org/lkml/20210429165941.27020-2-andraprs%40amazon.com/
- https://bugzilla.redhat.com/show_bug.cgi?id=1953022
