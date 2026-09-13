# [H] CVE-2020-14156

## Summary
Severity: High
Advisory: CVE-2020-14156
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-15
Source: https://osv.dev/vulnerability/CVE-2020-14156
Type: osv

## Details
user_channel/passwd_mgr.cpp in OpenBMC phosphor-host-ipmid before 2020-04-03 does not ensure that /etc/ipmi-pass has strong file permissions.

## References
- https://github.com/openbmc/openbmc/issues/3670
- https://lists.ozlabs.org/pipermail/openbmc/2020-June/022020.html
- https://github.com/openbmc/phosphor-host-ipmid/commit/b265455a2518ece7c004b43c144199ec980fc620
