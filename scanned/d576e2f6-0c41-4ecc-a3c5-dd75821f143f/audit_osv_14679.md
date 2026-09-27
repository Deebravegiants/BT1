# [M] CVE-2019-10740

## Summary
Severity: Medium
Advisory: CVE-2019-10740
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-04-07
Source: https://osv.dev/vulnerability/CVE-2019-10740
Type: osv

## Details
In Roundcube Webmail before 1.3.10, an attacker in possession of S/MIME or PGP encrypted emails can wrap them as sub-parts within a crafted multipart email. The encrypted part(s) can further be hidden using HTML/CSS or ASCII newline characters. This modified multipart email can be re-sent by the attacker to the intended receiver. If the receiver replies to this (benign looking) email, they unknowingly leak the plaintext of the encrypted message part(s) back to the attacker.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFFMSO5WKEYSGMTZPZFF4ZADUJ57PRN5/
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00083.html
- https://github.com/roundcube/roundcubemail/releases/tag/1.3.10
- https://github.com/roundcube/roundcubemail/issues/6638
