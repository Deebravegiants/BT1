# [M] CVE-2018-16869

## Summary
Severity: Medium
Advisory: CVE-2018-16869
CVSS: 5.7 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-16869
Type: osv

## Details
A Bleichenbacher type side-channel based padding oracle attack was found in the way nettle handles endian conversion of RSA decrypted PKCS#1 v1.5 data. An attacker who is able to run a process on the same physical core as the victim process, could use this flaw extract plaintext or in some cases downgrade any TLS connections to a vulnerable server.

## References
- http://cat.eyalro.net/
- http://www.securityfocus.com/bid/106092
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16869
