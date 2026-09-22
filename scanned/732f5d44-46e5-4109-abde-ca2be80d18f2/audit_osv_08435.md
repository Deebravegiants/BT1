# [H] CVE-2016-3180

## Summary
Severity: High
Advisory: CVE-2016-3180
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-07
Source: https://osv.dev/vulnerability/CVE-2016-3180
Type: osv

## Details
Tor Browser Launcher (aka torbrowser-launcher) before 0.2.4, during the initial run, allows man-in-the-middle attackers to bypass the PGP signature verification and execute arbitrary code via a Trojan horse tar file and a signature file with the valid tarball and signature.

## References
- http://www.securityfocus.com/bid/96140
- https://github.com/micahflee/torbrowser-launcher/issues/229
