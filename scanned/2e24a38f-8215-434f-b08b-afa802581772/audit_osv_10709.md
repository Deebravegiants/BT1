# [H] CVE-2017-18594

## Summary
Severity: High
Advisory: CVE-2017-18594
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2017-18594
Type: osv

## Details
nse_libssh2.cc in Nmap 7.70 is subject to a denial of service condition due to a double free when an SSH connection fails, as demonstrated by a leading \n character to ssh-brute.nse or ssh-auth-methods.nse.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00073.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00075.html
- https://github.com/AMatchandaHaystack/Research/blob/master/Nmap%26libsshDF
- https://seclists.org/nmap-announce/2019/0
- https://seclists.org/nmap-dev/2018/q2/45
- https://github.com/nmap/nmap/commit/350bbe0597d37ad67abe5fef8fba984707b4e9ad
- https://github.com/nmap/nmap/issues/1077
- https://github.com/nmap/nmap/issues/1227
