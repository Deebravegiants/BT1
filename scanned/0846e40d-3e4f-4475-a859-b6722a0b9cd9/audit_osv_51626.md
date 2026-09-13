# [M] CVE-2021-3635

## Summary
Severity: Medium
Advisory: CVE-2021-3635
Aliases: A-197614484, PUB-A-197614484
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-13
Source: https://osv.dev/vulnerability/CVE-2021-3635
Type: osv

## Details
A flaw was found in the Linux kernel netfilter implementation in versions prior to 5.5-rc7. A user with root (CAP_SYS_ADMIN) access is able to panic the system when issuing netfilter netflow commands.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1976946
