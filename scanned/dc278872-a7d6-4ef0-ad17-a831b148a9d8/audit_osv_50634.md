# [M] CVE-2020-26541

## Summary
Severity: Medium
Advisory: CVE-2020-26541
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-26541
Type: osv

## Details
The Linux kernel through 5.8.13 does not properly enforce the Secure Boot Forbidden Signature Database (aka dbx) protection mechanism. This affects certs/blacklist.c and certs/system_keyring.c.

## References
- https://lkml.org/lkml/2020/9/15/1871
