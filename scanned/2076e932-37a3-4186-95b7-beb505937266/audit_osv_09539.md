# [H] CVE-2017-1000097

## Summary
Severity: High
Advisory: CVE-2017-1000097
Aliases: GO-2022-0171
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000097
Type: osv

## Details
On Darwin, user's trust preferences for root certificates were not honored. If the user had a root certificate loaded in their Keychain that was explicitly not trusted, a Go program would still verify a connection using that root certificate.

## References
- https://go-review.googlesource.com/c/33721/
- https://groups.google.com/forum/#%21msg/golang-dev/4NdLzS8sls8/uIz8QlnIBQAJ
- https://github.com/golang/go/issues/18141
