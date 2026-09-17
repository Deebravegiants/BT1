# [M] CVE-2016-1252

## Summary
Severity: Medium
Advisory: CVE-2016-1252
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-12-05
Source: https://osv.dev/vulnerability/CVE-2016-1252
Type: osv

## Details
The apt package in Debian jessie before 1.0.9.8.4, in Debian unstable before 1.4~beta2, in Ubuntu 14.04 LTS before 1.0.1ubuntu2.17, in Ubuntu 16.04 LTS before 1.2.15ubuntu0.2, and in Ubuntu 16.10 before 1.3.2ubuntu0.1 allows man-in-the-middle attackers to bypass a repository-signing protection mechanism by leveraging improper error handling when validating InRelease file signatures.

## References
- http://www.ubuntu.com/usn/USN-3156-1
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1020
- https://bugs.launchpad.net/ubuntu/+source/apt/+bug/1647467
- https://www.debian.org/security/2016/dsa-3733
- https://www.exploit-db.com/exploits/40916/
- http://packetstormsecurity.com/files/140145/apt-Repository-Signing-Bypass.html
