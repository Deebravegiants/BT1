# [M] Perl threads have a working directory race condition where file operations may target unintended paths

## Summary
Severity: Medium
Advisory: CVE-2025-40909
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-05-30
Source: https://osv.dev/vulnerability/CVE-2025-40909
Type: osv

## Details
Perl threads have a working directory race condition where file operations may target unintended paths.

If a directory handle is open at thread creation, the process-wide current working directory is temporarily changed in order to clone that handle for the new thread, which is visible from any third (or more) thread already running. 

This may lead to unintended operations such as loading code or accessing files from unexpected locations, which a local attacker may be able to exploit.

The bug was introduced in commit 11a11ecf4bea72b17d250cfb43c897be1341861e and released in Perl version 5.13.6

## References
- http://seclists.org/fulldisclosure/2025/Sep/53
- http://seclists.org/fulldisclosure/2025/Sep/54
- http://seclists.org/fulldisclosure/2025/Sep/55
- http://www.openwall.com/lists/oss-security/2025/05/23/1
- http://www.openwall.com/lists/oss-security/2025/05/30/4
- http://www.openwall.com/lists/oss-security/2025/06/02/2
- http://www.openwall.com/lists/oss-security/2025/06/02/5
- http://www.openwall.com/lists/oss-security/2025/06/02/6
- http://www.openwall.com/lists/oss-security/2025/06/02/7
- http://www.openwall.com/lists/oss-security/2025/06/03/1
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1098226
- https://cpan.org/modules
- https://lists.debian.org/debian-lts-announce/2026/04/msg00018.html
- https://perldoc.perl.org/5.14.0/perl5136delta#Directory-handles-not-copied-to-threads
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40909.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40909
- https://github.com/Perl/perl5/issues/10387
- https://github.com/Perl/perl5/issues/23010
- https://github.com/Perl/perl5/commit/11a11ecf4bea72b17d250cfb43c897be1341861e
- https://github.com/Perl/perl5/commit/918bfff86ca8d6d4e4ec5b30994451e0bd74aba9.patch
