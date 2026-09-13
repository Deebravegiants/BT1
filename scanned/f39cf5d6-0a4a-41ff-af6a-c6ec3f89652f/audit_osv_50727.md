# [H] CVE-2020-35519

## Summary
Severity: High
Advisory: CVE-2020-35519
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-35519
Type: osv

## Details
An out-of-bounds (OOB) memory access flaw was found in x25_bind in net/x25/af_x25.c in the Linux kernel version v5.12-rc5. A bounds check failure allows a local attacker with a user account on the system to gain access to out-of-bounds memory, leading to a system crash or a leak of internal kernel information. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.netapp.com/advisory/ntap-20210618-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=1908251
