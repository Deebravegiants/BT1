# [M] CVE-2017-18016

## Summary
Severity: Medium
Advisory: CVE-2017-18016
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/CVE-2017-18016
Type: osv

## Details
Parity Browser 1.6.10 and earlier allows remote attackers to bypass the Same Origin Policy and obtain sensitive information by requesting other websites via the Parity web proxy engine (reusing the current website's token, which is not bound to an origin).

## References
- https://github.com/paritytech/parity/commit/53609f703e2f1af76441344ac3b72811c726a215
- http://www.openwall.com/lists/oss-security/2018/01/10/1
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2017-18016
- https://www.exploit-db.com/exploits/43499/
