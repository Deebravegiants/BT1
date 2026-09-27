# [M] CVE-2017-7526

## Summary
Severity: Medium
Advisory: CVE-2017-7526
CVSS: 6.8 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-7526
Type: osv

## Details
libgcrypt before version 1.7.8 is vulnerable to a cache side-channel attack resulting into a complete break of RSA-1024 while using the left-to-right method for computing the sliding-window expansion. The same attack is believed to work on RSA-2048 with moderately more computation. This side-channel requires that attacker can run arbitrary software on the hardware where the private RSA key is used.

## References
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=78130828e9a140a9de4dafadbc844dbb64cb709a
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=8725c99ffa41778f382ca97233183bcd687bb0ce
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=e6a3dc9900433bbc8ad362a595a3837318c28fa9
- http://www.securityfocus.com/bid/99338
- http://www.securitytracker.com/id/1038915
- https://eprint.iacr.org/2017/627
- https://lists.gnupg.org/pipermail/gnupg-announce/2017q2/000408.html
- https://usn.ubuntu.com/3733-1/
- https://usn.ubuntu.com/3733-2/
- https://www.debian.org/security/2017/dsa-3901
- https://www.debian.org/security/2017/dsa-3960
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7526
