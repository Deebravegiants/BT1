# [C] CVE-2019-15522

## Summary
Severity: Critical
Advisory: CVE-2019-15522
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2019-15522
Type: osv

## Details
An issue was discovered in LINBIT csync2 through 2.0. csync_daemon_session in daemon.c neglects to force a failure of a hello command when the configuration requires use of SSL.

## References
- https://github.com/LINBIT/csync2/commit/416f1de878ef97e27e27508914f7ba8599a0be22
