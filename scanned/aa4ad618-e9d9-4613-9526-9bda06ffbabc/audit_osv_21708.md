# [C] CVE-2021-45809

## Summary
Severity: Critical
Advisory: CVE-2021-45809
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-22
Source: https://osv.dev/vulnerability/CVE-2021-45809
Type: osv

## Details
GlobalProtect-openconnect versions prior to 1.4.3 are affected by incorrect access control in GPService through DBUS, GUI Application. The way GlobalProtect-Openconnect is set up enables arbitrary users to execute commands as root by submitting the `--script=<script>` parameter.

## References
- https://github.com/yuezk/GlobalProtect-openconnect/issues/113
