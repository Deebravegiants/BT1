# [M] CVE-2020-10742

## Summary
Severity: Medium
Advisory: CVE-2020-10742
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-10742
Type: osv

## Details
A flaw was found in the Linux kernel. An index buffer overflow during Direct IO write leading to the NFS client to crash. In some cases, a reach out of the index after one memory allocation by kmalloc will cause a kernel panic. The highest threat from this vulnerability is to data confidentiality and system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1835127
