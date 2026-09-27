# [C] CVE-2017-15041

## Summary
Severity: Critical
Advisory: CVE-2017-15041
Aliases: GO-2022-0177
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-15041
Type: osv

## Details
Go before 1.8.4 and 1.9.x before 1.9.1 allows "go get" remote command execution. Using custom domains, it is possible to arrange things so that example.com/pkg1 points to a Subversion repository but example.com/pkg1/pkg2 points to a Git repository. If the Subversion repository includes a Git checkout in its pkg2 directory and some other work is done to ensure the proper ordering of operations, "go get" can be tricked into reusing this Git checkout for the fetch of code from pkg2. If the Subversion repository's Git checkout has malicious commands in .git/hooks/, they will execute on the system running "go get."

## References
- http://www.securityfocus.com/bid/101196
- https://access.redhat.com/errata/RHSA-2017:3463
- https://access.redhat.com/errata/RHSA-2018:0878
- https://groups.google.com/d/msg/golang-dev/RinSE3EiJBI/kYL7zb07AgAJ
- https://lists.debian.org/debian-lts-announce/2021/03/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00015.html
- https://security.gentoo.org/glsa/201710-23
- https://github.com/golang/go/issues/22125
- https://golang.org/cl/68022
- https://golang.org/cl/68190
