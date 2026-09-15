# [H] CVE-2020-28852

## Summary
Severity: High
Advisory: CVE-2020-28852
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-01-02
Source: https://osv.dev/vulnerability/CVE-2020-28852
Type: osv

## Details
In x/text in Go before v0.3.5, a "slice bounds out of range" panic occurs in language.ParseAcceptLanguage while processing a BCP 47 tag. (x/text/language is supposed to be able to parse an HTTP Accept-Language header.)

## References
- https://security.netapp.com/advisory/ntap-20210212-0004/
- https://github.com/golang/go/issues/42536
