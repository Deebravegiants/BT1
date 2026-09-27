# [C] CVE-2018-1000178

## Summary
Severity: Critical
Advisory: CVE-2018-1000178
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2018-1000178
Type: osv

## Details
A heap corruption of type CWE-120 exists in quassel version 0.12.4 in quasselcore in void DataStreamPeer::processMessage(const QByteArray &msg) datastreampeer.cpp line 62 that allows an attacker to execute code remotely.

## References
- https://usn.ubuntu.com/4594-1/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00001.html
- https://security.gentoo.org/glsa/201806-04
- https://www.debian.org/security/2018/dsa-4189
- https://github.com/quassel/quassel/blob/master/src/common/protocols/datastream/datastreampeer.cpp#L62
- https://i.imgur.com/JJ4QcNq.png
