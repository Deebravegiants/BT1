# [H] CVE-2019-13139

## Summary
Severity: High
Advisory: CVE-2019-13139
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-22
Source: https://osv.dev/vulnerability/CVE-2019-13139
Type: osv

## Details
In Docker before 18.09.4, an attacker who is capable of supplying or manipulating the build path for the "docker build" command would be able to gain command execution. An issue exists in the way "docker build" processes remote git URLs, and results in command injection into the underlying "git clone" command, leading to code execution in the context of the user executing the "docker build" command. This occurs because git ref can be misinterpreted as a flag.

## References
- https://seclists.org/bugtraq/2019/Sep/21
- https://access.redhat.com/errata/RHBA-2019:3092
- https://docs.docker.com/engine/release-notes/#18094
- https://security.netapp.com/advisory/ntap-20190910-0001/
- https://www.debian.org/security/2019/dsa-4521
- https://github.com/moby/moby/pull/38944
- https://staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/
