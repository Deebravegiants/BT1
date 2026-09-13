# [M] CVE-2022-42324

## Summary
Severity: Medium
Advisory: CVE-2022-42324
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/CVE-2022-42324
Type: osv

## Details
Oxenstored 32->31 bit integer truncation issues Integers in Ocaml are 63 or 31 bits of signed precision. The Ocaml Xenbus library takes a C uint32_t out of the ring and casts it directly to an Ocaml integer. In 64-bit Ocaml builds this is fine, but in 32-bit builds, it truncates off the most significant bit, and then creates unsigned/signed confusion in the remainder. This in turn can feed a negative value into logic not expecting a negative value, resulting in unexpected exceptions being thrown. The unexpected exception is not handled suitably, creating a busy-loop trying (and failing) to take the bad packet out of the xenstore ring.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTMITQBGC23MSDHUCAPCVGLMVXIBXQTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZVXG7OOOXCX6VIPEMLFDPIPUTFAYWPE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLI2NPNEH7CNJO3VZGQNOI4M4EWLNKPZ/
- https://security.gentoo.org/glsa/202402-07
- https://www.debian.org/security/2022/dsa-5272
- http://www.openwall.com/lists/oss-security/2022/11/01/10
- http://xenbits.xen.org/xsa/advisory-420.html
- https://xenbits.xenproject.org/xsa/advisory-420.txt
