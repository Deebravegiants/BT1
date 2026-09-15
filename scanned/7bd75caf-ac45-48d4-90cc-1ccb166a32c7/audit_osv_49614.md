# [M] CVE-2019-14664

## Summary
Severity: Medium
Advisory: CVE-2019-14664
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-08-05
Source: https://osv.dev/vulnerability/CVE-2019-14664
Type: osv

## Details
In Enigmail below 2.1, an attacker in possession of PGP encrypted emails can wrap them as sub-parts within a crafted multipart email. The encrypted part(s) can further be hidden using HTML/CSS or ASCII newline characters. This modified multipart email can be re-sent by the attacker to the intended receiver. If the receiver replies to this (benign looking) email, he unknowingly leaks the plaintext of the encrypted message part(s) back to the attacker. This attack variant bypasses protection mechanisms implemented after the "EFAIL" attacks.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GHC5WDQ47FQSL5CTGQUYIHVC3RNZ7UH5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AVNTEF3WSOOQYKMIPEH7F77UPXES5BU5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CYWBJHSBBLAHKMRWDWH2XXQDYAGDHB5I/
- https://www.enigmail.net/index.php/en/download/changelog
- https://sourceforge.net/p/enigmail/bugs/984/
