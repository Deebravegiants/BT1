# [M] CVE-2018-16868

## Summary
Severity: Medium
Advisory: CVE-2018-16868
CVSS: 5.6 (CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-16868
Type: osv

## Details
A Bleichenbacher type side-channel based padding oracle attack was found in the way gnutls handles verification of RSA decrypted PKCS#1 v1.5 data. An attacker who is able to run process on the same physical core as the victim process, could use this to extract plaintext or in some cases downgrade any TLS connections to a vulnerable server.

## References
- http://cat.eyalro.net/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00068.html
- http://www.securityfocus.com/bid/106080
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16868
