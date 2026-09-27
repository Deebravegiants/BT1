# [M] CVE-2017-1000385

## Summary
Severity: Medium
Advisory: CVE-2017-1000385
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-12-12
Source: https://osv.dev/vulnerability/CVE-2017-1000385
Type: osv

## Details
The Erlang otp TLS server answers with different TLS alerts to different error types in the RSA PKCS #1 1.5 padding. This allows an attacker to decrypt content or sign messages with the server's private key (this is a variation of the Bleichenbacher attack).

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00010.html
- https://usn.ubuntu.com/3571-1/
- http://www.securityfocus.com/bid/102197
- https://access.redhat.com/errata/RHSA-2018:0242
- https://access.redhat.com/errata/RHSA-2018:0303
- https://access.redhat.com/errata/RHSA-2018:0368
- https://access.redhat.com/errata/RHSA-2018:0528
- http://erlang.org/pipermail/erlang-questions/2017-November/094255.html
- http://erlang.org/pipermail/erlang-questions/2017-November/094256.html
- http://erlang.org/pipermail/erlang-questions/2017-November/094257.html
- https://robotattack.org/
- https://www.debian.org/security/2017/dsa-4057
- https://www.kb.cert.org/vuls/id/144389
