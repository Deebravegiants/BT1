# [C] CVE-2016-10253

## Summary
Severity: Critical
Advisory: CVE-2016-10253
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-18
Source: https://osv.dev/vulnerability/CVE-2016-10253
Type: osv

## Details
An issue was discovered in Erlang/OTP 18.x. Erlang's generation of compiled regular expressions is vulnerable to a heap overflow. Regular expressions using a malformed extpattern can indirectly specify an offset that is used as an array index. This ordinal permits arbitrary regions within the erts_alloc arena to be both read and written to.

## References
- https://github.com/erlang/otp/pull/1108
- https://usn.ubuntu.com/3571-1/
