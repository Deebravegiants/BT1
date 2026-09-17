# [H] CVE-2017-7651

## Summary
Severity: High
Advisory: CVE-2017-7651
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-7651
Type: osv

## Details
In Eclipse Mosquitto 1.4.14, a user can shutdown the Mosquitto server simply by filling the RAM memory with a lot of connections with large payload. This can be done without authentications if occur in connection phase of MQTT protocol.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00037.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00016.html
- https://www.debian.org/security/2018/dsa-4325
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=529754
- https://mosquitto.org/blog/2018/02/security-advisory-cve-2017-7651-cve-2017-7652/
