# [M] CVE-2020-29568

## Summary
Severity: Medium
Advisory: CVE-2020-29568
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29568
Type: osv

## Details
An issue was discovered in Xen through 4.14.x. Some OSes (such as Linux, FreeBSD, and NetBSD) are processing watch events using a single thread. If the events are received faster than the thread is able to handle, they will get queued. As the queue is unbounded, a guest may be able to trigger an OOM in the backend. All systems with a FreeBSD, Linux, or NetBSD (any version) dom0 are vulnerable.

## References
- https://security.gentoo.org/glsa/202107-30
- https://www.debian.org/security/2021/dsa-4843
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://xenbits.xenproject.org/xsa/advisory-349.html
