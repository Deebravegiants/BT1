# [M] CVE-2019-11779

## Summary
Severity: Medium
Advisory: CVE-2019-11779
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-11779
Type: osv

## Details
In Eclipse Mosquitto 1.5.0 to 1.6.5 inclusive, if a malicious MQTT client sends a SUBSCRIBE packet containing a topic that consists of approximately 65400 or more '/' characters, i.e. the topic hierarchy separator, then a stack overflow will occur.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D4WMHIM64Q35NGTR6R3ILZUL4MA4ANB5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HFWQBNFTAVHPUYNGYO2TCPF5PCSWC2Z7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWNVTFA2CKXERXRYPYE2YFTZP4GNBGYY/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00077.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00008.html
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=551160
- https://lists.debian.org/debian-lts-announce/2019/10/msg00035.html
- https://seclists.org/bugtraq/2019/Nov/25
- https://usn.ubuntu.com/4137-1/
- https://www.debian.org/security/2019/dsa-4570
