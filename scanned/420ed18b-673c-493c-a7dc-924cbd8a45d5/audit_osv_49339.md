# [M] CVE-2019-10224

## Summary
Severity: Medium
Advisory: CVE-2019-10224
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-11-25
Source: https://osv.dev/vulnerability/CVE-2019-10224
Type: osv

## Details
A flaw has been found in 389-ds-base versions 1.4.x.x before 1.4.1.3. When executed in verbose mode, the dscreate and dsconf commands may display sensitive information, such as the Directory Manager password. An attacker, able to see the screen or record the terminal standard error output, could use this flaw to gain sensitive information.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://pagure.io/389-ds-base/issue/50251
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10224
