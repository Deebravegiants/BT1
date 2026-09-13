# [H] CVE-2016-6129

## Summary
Severity: High
Advisory: CVE-2016-6129
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-6129
Type: osv

## Details
The rsa_verify_hash_ex function in rsa_verify_hash.c in LibTomCrypt, as used in OP-TEE before 2.2.0, does not validate that the message length is equal to the ASN.1 encoded data length, which makes it easier for remote attackers to forge RSA signatures or public certificates by leveraging a Bleichenbacher signature forgery attack.

## References
- https://www.op-tee.org/advisories/
- https://bugzilla.redhat.com/show_bug.cgi?id=1370955
- https://github.com/libtom/libtomcrypt/commit/5eb9743410ce4657e9d54fef26a2ee31a1b5dd0
