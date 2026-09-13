# [H] CVE-2017-14229

## Summary
Severity: High
Advisory: CVE-2017-14229
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14229
Type: osv

## Details
There is an infinite loop in the jpc_dec_tileinit function in jpc/jpc_dec.c of Jasper 2.0.13. It will lead to a remote denial of service attack.

## References
- http://www.securityfocus.com/bid/100861
- https://github.com/mdadams/jasper/issues/146
- https://security.gentoo.org/glsa/201908-03
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
