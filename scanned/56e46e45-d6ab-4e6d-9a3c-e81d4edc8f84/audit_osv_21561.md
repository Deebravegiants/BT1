# [H] CVE-2021-44038

## Summary
Severity: High
Advisory: CVE-2021-44038
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-19
Source: https://osv.dev/vulnerability/CVE-2021-44038
Type: osv

## Details
An issue was discovered in Quagga through 1.2.4. Unsafe chown/chmod operations in the suggested spec file allow users (with control of the non-root-owned directory /etc/quagga) to escalate their privileges to root upon package installation or update.

## References
- https://github.com/Quagga/quagga/releases
- https://bugzilla.suse.com/show_bug.cgi?id=1191890
