# [H] CVE-2016-3995

## Summary
Severity: High
Advisory: CVE-2016-3995
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-02-13
Source: https://osv.dev/vulnerability/CVE-2016-3995
Type: osv

## Details
The timing attack protection in Rijndael::Enc::ProcessAndXorBlock and Rijndael::Dec::ProcessAndXorBlock in Crypto++ (aka cryptopp) before 5.6.4 may be optimized out by the compiler, which allows attackers to conduct timing attacks.

## References
- http://www.securityfocus.com/bid/85975
- http://www.openwall.com/lists/oss-security/2016/04/11/2
- https://github.com/weidai11/cryptopp/issues/146
