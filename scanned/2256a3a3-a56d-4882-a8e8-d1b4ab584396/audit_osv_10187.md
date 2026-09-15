# [H] CVE-2017-14178

## Summary
Severity: High
Advisory: CVE-2017-14178
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-02
Source: https://osv.dev/vulnerability/CVE-2017-14178
Type: osv

## Details
In snapd 2.27 through 2.29.2 the 'snap logs' command could be made to call journalctl without match arguments and therefore allow unprivileged, unauthenticated users to bypass systemd-journald's access restrictions.

## References
- https://github.com/snapcore/snapd/pull/4194
- https://launchpad.net/bugs/1730255
- https://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-14178.html
