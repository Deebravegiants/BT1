# [H] CVE-2020-10030

## Summary
Severity: High
Advisory: CVE-2020-10030
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-10030
Type: osv

## Details
An issue has been found in PowerDNS Recursor 4.1.0 up to and including 4.3.0. It allows an attacker (with enough privileges to change the system's hostname) to cause disclosure of uninitialized memory content via a stack-based out-of-bounds read. It only occurs on systems where gethostname() does not have '\0' termination of the returned string if the hostname is larger than the supplied buffer. (Linux systems are not affected because the buffer is always large enough. OpenBSD systems are not affected because the returned hostname always has '\0' termination.) Under some conditions, this issue can lead to the writing of one '\0' byte out-of-bounds on the stack, causing a denial of service or possibly arbitrary code execution.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00052.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMP72NJGKBWR5WEBXAWX5KSLQUDFTG6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PS4ZN5XGENYNFKX7QIIOUCQQHXE37GJF/
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2020-03.html
