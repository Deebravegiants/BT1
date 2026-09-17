# [H] CVE-2020-7670

## Summary
Severity: High
Advisory: CVE-2020-7670
Aliases: SNYK-RUBY-AGOO-569137
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-06-10
Source: https://osv.dev/vulnerability/CVE-2020-7670
Type: osv

## Details
agoo prior to 2.14.0 allows request smuggling attacks where agoo is used as a backend and a frontend proxy also being vulnerable. HTTP pipelining issues and request smuggling attacks might be possible due to incorrect Content-Length and Transfer encoding header parsing. It is possible to conduct HTTP request smuggling attacks where `agoo` is used as part of a chain of backend servers due to insufficient `Content-Length` and `Transfer Encoding` parsing.

## References
- https://snyk.io/vuln/SNYK-RUBY-AGOO-569137
- https://github.com/ohler55/agoo/issues/88
- https://github.com/ohler55/agoo/commit/23d03535cf7b50d679a60a953a0cae9519a4a130
