# [M] CVE-2019-15718

## Summary
Severity: Medium
Advisory: CVE-2019-15718
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15718
Type: osv

## Details
In systemd 240, bus_open_system_watch_bind_with_description in shared/bus-util.c (as used by systemd-resolved to connect to the system D-Bus instance), calls sd_bus_set_trusted, which disables access controls for incoming D-Bus messages. An unprivileged user can exploit this by executing D-Bus methods that should be restricted to privileged users, in order to change the system's DNS resolver settings.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BRE5IS24XTF5WNZGH2L7GSQJKARBOEGL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIKGKXZ5OEGOEYURHLJHEMFYNLEGAW5B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U2WNHRJW4XI6H5YMDG4BUFGPAXWUMUVG/
- https://access.redhat.com/errata/RHSA-2019:3592
- https://access.redhat.com/errata/RHSA-2019:3941
- https://bugzilla.redhat.com/show_bug.cgi?id=1746057
- http://www.openwall.com/lists/oss-security/2019/09/03/1
