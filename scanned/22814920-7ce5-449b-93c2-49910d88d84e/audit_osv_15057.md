# [C] CVE-2019-13132

## Summary
Severity: Critical
Advisory: CVE-2019-13132
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2019-13132
Type: osv

## Details
In ZeroMQ libzmq before 4.0.9, 4.1.x before 4.1.7, and 4.2.x before 4.3.2, a remote, unauthenticated client connecting to a libzmq application, running with a socket listening with CURVE encryption/authentication enabled, may cause a stack overflow and overwrite the stack with arbitrary data, due to a buffer overflow in the library. Users running public servers with the above configuration are highly encouraged to upgrade as soon as possible, as there are no known mitigations.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00033.html
- https://fangpenlin.com/posts/2024/04/07/how-i-discovered-a-9-point-8-critical-security-vulnerability-in-zeromq-with-mostly-pure-luck/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AVCTNUEOFFZUNJOXFCYCF3C6Y6NDILI3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MK7SJYDJ7MMRRRPCUN3SCSE7YK6ZSHVS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T6HINI24SL7CU6XIJWUOSGTZWEFOOL7X/
- https://news.ycombinator.com/item?id=39970716
- http://www.openwall.com/lists/oss-security/2019/07/08/6
- http://www.securityfocus.com/bid/109284
- https://github.com/zeromq/libzmq/issues/3558
- https://github.com/zeromq/libzmq/releases
- https://lists.debian.org/debian-lts-announce/2019/07/msg00007.html
- https://seclists.org/bugtraq/2019/Jul/13
- https://security.gentoo.org/glsa/201908-17
- https://usn.ubuntu.com/4050-1/
- https://www.debian.org/security/2019/dsa-4477
