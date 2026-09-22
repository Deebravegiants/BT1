# [H] CVE-2019-1000014

## Summary
Severity: High
Advisory: CVE-2019-1000014
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/CVE-2019-1000014
Type: osv

## Details
Erlang/OTP Rebar3 version 3.7.0 through 3.7.5 contains a Signing oracle vulnerability in Package registry verification that can result in Package modifications not detected, allowing code execution. This attack appears to be exploitable via Victim fetches packages from malicious/compromised mirror. This vulnerability appears to have been fixed in 3.8.0.

## References
- https://github.com/erlang/rebar3/pull/1986
