# [M] Golang/x/crypto message forgery vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x3jr-pf6g-c48f
CVE: CVE-2019-11841
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x3jr-pf6g-c48f
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.0.0-20190424203555-c05e17bb3b2d

## Details
A message-forgery issue was discovered in `crypto/openpgp/clearsign/clearsign.go` in supplementary Go cryptography libraries 2019-03-25. According to the OpenPGP Message Format specification in RFC 4880 chapter 7, a cleartext signed message can contain one or more optional "Hash" Armor Headers. The "Hash" Armor Header specifies the message digest algorithm(s) used for the signature. However, the Go clearsign package ignores the value of this header, which allows an attacker to spoof it. Consequently, an attacker can lead a victim to believe the signature was generated using a different message digest algorithm than what was actually used. Moreover, since the library skips Armor Header parsing in general, an attacker can not only embed arbitrary Armor Headers, but also prepend arbitrary text to cleartext messages without invalidating the signatures.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11841
- https://github.com/golang/crypto/commit/c05e17bb3b2dca130fc919668a96b4bec9eb9442
- https://github.com/golang/crypto/tree/master/openpgp/clearsign
- https://go-review.git.corp.google.com/c/crypto/+/173778
- https://go.googlesource.com/crypto/+/c05e17bb3b2dca130fc919668a96b4bec9eb9442
- https://groups.google.com/d/msg/golang-openpgp/6vdgZoTgbIY/K6bBY9z3DAAJ
- https://lists.debian.org/debian-lts-announce/2019/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00014.html
- https://lists.debian.org/debian-lts-announce/2023/06/msg00017.html
- https://pkg.go.dev/vuln/GO-2023-1992
- https://web.archive.org/web/20201207161832/https://sec-consult.com/en/blog/advisories/cleartext-message-spoofing-in-go-cryptography-libraries-cve-2019-11841
- http://packetstormsecurity.com/files/152840/Go-Cryptography-Libraries-Cleartext-Message-Spoofing.html
