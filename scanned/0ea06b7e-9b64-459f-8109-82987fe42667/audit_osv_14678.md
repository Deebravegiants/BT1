# [M] CVE-2019-10734

## Summary
Severity: Medium
Advisory: CVE-2019-10734
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2019-04-07
Source: https://osv.dev/vulnerability/CVE-2019-10734
Type: osv

## Details
In KDE Trojita 0.7, an attacker in possession of S/MIME or PGP encrypted emails can wrap them as sub-parts within a crafted multipart email. The encrypted part(s) can further be hidden using HTML/CSS or ASCII newline characters. This modified multipart email can be re-sent by the attacker to the intended receiver. If the receiver replies to this (benign looking) email, they unknowingly leak the plaintext of the encrypted message part(s) back to the attacker.

## References
- https://bugs.kde.org/show_bug.cgi?id=404697
