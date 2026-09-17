# [H] CVE-2017-1000200

## Summary
Severity: High
Advisory: CVE-2017-1000200
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/CVE-2017-1000200
Type: osv

## Details
tcmu-runner version 1.0.5 to 1.2.0 is vulnerable to a dbus triggered NULL pointer dereference in the tcmu-runner daemon's on_unregister_handler() function resulting in denial of service

## References
- https://access.redhat.com/errata/RHSA-2017:3277
- https://github.com/open-iscsi/tcmu-runner/pull/200/commits/bb80e9c7a798f035768260ebdadffb6eb0786178
