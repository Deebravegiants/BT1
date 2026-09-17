# [M] CVE-2020-12862

## Summary
Severity: Medium
Advisory: CVE-2020-12862
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CVE-2020-12862
Type: osv

## Details
An out-of-bounds read in SANE Backends before 1.0.30 may allow a malicious device connected to the same local network as the victim to read important information, such as the ASLR offsets of the program, aka GHSL-2020-082.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00079.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00003.html
- https://alioth-lists.debian.net/pipermail/sane-announce/2020/000041.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00010.html
- https://usn.ubuntu.com/4470-1/
- https://securitylab.github.com/advisories/GHSL-2020-075-libsane
