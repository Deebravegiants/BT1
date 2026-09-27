# [H] CVE-2017-7654

## Summary
Severity: High
Advisory: CVE-2017-7654
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-05
Source: https://osv.dev/vulnerability/CVE-2017-7654
Type: osv

## Details
In Eclipse Mosquitto 1.4.15 and earlier, a Memory Leak vulnerability was found within the Mosquitto Broker. Unauthenticated clients can send crafted CONNECT packets which could cause a denial of service in the Mosquitto Broker.

## References
- https://usn.ubuntu.com/4023-1/
- https://lists.debian.org/debian-lts-announce/2018/09/msg00036.html
- https://www.debian.org/security/2018/dsa-4325
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=533493
