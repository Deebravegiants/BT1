# [M] CVE-2017-8932

## Summary
Severity: Medium
Advisory: CVE-2017-8932
Aliases: GO-2022-0187
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-07-06
Source: https://osv.dev/vulnerability/CVE-2017-8932
Type: osv

## Details
A bug in the standard library ScalarMult implementation of curve P-256 for amd64 architectures in Go before 1.7.6 and 1.8.x before 1.8.2 causes incorrect results to be generated for specific input points. An adaptive attack can be mounted to progressively extract the scalar input to ScalarMult by submitting crafted points and observing failures to the derive correct output. This leads to a full key recovery attack against static ECDH, as used in popular JWT libraries.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LZH4T47ROLZ6YEZBDVXVS2KISTDMXAPS/
- https://access.redhat.com/errata/RHSA-2017:1859
- https://github.com/golang/go/issues/20040
- https://go-review.googlesource.com/c/41070/
- https://groups.google.com/d/msg/golang-announce/B5ww0iFt1_Q/TgUFJV14BgAJ
- https://bugzilla.redhat.com/show_bug.cgi?id=1455191
- http://lists.opensuse.org/opensuse-updates/2017-06/msg00079.html
- http://lists.opensuse.org/opensuse-updates/2017-06/msg00080.html
- https://github.com/golang/go/commit/9294fa2749ffee7edbbb817a0ef9fe633136fa9c
