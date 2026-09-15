# [H] CVE-2017-7652

## Summary
Severity: High
Advisory: CVE-2017-7652
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-25
Source: https://osv.dev/vulnerability/CVE-2017-7652
Type: osv

## Details
In Eclipse Mosquitto 1.4.14, if a Mosquitto instance is set running with a configuration file, then sending a HUP signal to server triggers the configuration to be reloaded from disk. If there are lots of clients connected so that there are no more file descriptors/sockets available (default limit typically 1024 file descriptors on Linux), then opening the configuration file will fail.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00037.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00016.html
- https://www.debian.org/security/2018/dsa-4325
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=530102
- https://mosquitto.org/blog/2018/02/security-advisory-cve-2017-7651-cve-2017-7652/
