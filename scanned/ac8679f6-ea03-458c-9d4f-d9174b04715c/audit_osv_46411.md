# [H] CVE-2009-5155

## Summary
Severity: High
Advisory: CVE-2009-5155
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-26
Source: https://osv.dev/vulnerability/CVE-2009-5155
Type: osv

## Details
In the GNU C Library (aka glibc or libc6) before 2.28, parse_reg_exp in posix/regcomp.c misparses alternatives, which allows attackers to cause a denial of service (assertion failure and application exit) or trigger an incorrect result by attempting a regular-expression match.

## References
- http://git.savannah.gnu.org/cgit/gnulib.git/commit/?id=5513b40999149090987a0341c018d05d3eea1272
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=22793
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=32806
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34238
- https://security.netapp.com/advisory/ntap-20190315-0002/
- https://sourceware.org/bugzilla/show_bug.cgi?id=11053
- https://sourceware.org/bugzilla/show_bug.cgi?id=18986
- http://git.savannah.gnu.org/cgit/gnulib.git/commit/?id=5513b40999149090987a0341c018d05d3eea1272
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=22793
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=32806
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34238
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=32806
- https://debbugs.gnu.org/cgi/bugreport.cgi?bug=34238
- https://sourceware.org/bugzilla/show_bug.cgi?id=11053
- https://sourceware.org/bugzilla/show_bug.cgi?id=18986
- http://git.savannah.gnu.org/cgit/gnulib.git/commit/?id=5513b40999149090987a0341c018d05d3eea1272
- https://security.netapp.com/advisory/ntap-20190315-0002/
- https://sourceware.org/bugzilla/show_bug.cgi?id=11053
- https://sourceware.org/bugzilla/show_bug.cgi?id=18986
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
