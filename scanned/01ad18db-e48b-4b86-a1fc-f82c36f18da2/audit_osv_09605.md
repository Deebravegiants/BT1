# [M] CVE-2017-1000369

## Summary
Severity: Medium
Advisory: CVE-2017-1000369
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-06-19
Source: https://osv.dev/vulnerability/CVE-2017-1000369
Type: osv

## Details
Exim supports the use of multiple "-p" command line arguments which are malloc()'ed and never free()'ed, used in conjunction with other issues allows attackers to cause arbitrary code execution. This affects exim version 4.89 and earlier. Please note that at this time upstream has released a patch (commit 65e061b76867a9ea7aeeb535341b790b90ae6c21), but it is not known if a new point release is available that addresses this issue at this time.

## References
- http://www.debian.org/security/2017/dsa-3888
- http://www.securityfocus.com/bid/99252
- http://www.securitytracker.com/id/1038779
- https://access.redhat.com/security/cve/CVE-2017-1000369
- https://security.gentoo.org/glsa/201709-19
- https://www.qualys.com/2017/06/19/stack-clash/stack-clash.txt
- https://github.com/Exim/exim/commit/65e061b76867a9ea7aeeb535341b790b90ae6c21
