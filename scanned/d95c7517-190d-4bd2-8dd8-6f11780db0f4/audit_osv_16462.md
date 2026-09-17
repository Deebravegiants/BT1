# [H] CVE-2019-7167

## Summary
Severity: High
Advisory: CVE-2019-7167
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-7167
Type: osv

## Details
Zcash, before the Sapling network upgrade (2018-10-28), had a counterfeiting vulnerability. A key-generation process, during evaluation of polynomials related to a to-be-proven statement, produced certain bypass elements. Availability of these elements allowed a cheating prover to bypass a consistency check, and consequently transform the proof of one statement into an ostensibly valid proof of a different statement, thereby breaking the soundness of the proof system. This misled the original Sprout zk-SNARK verifier into accepting the correctness of a transaction.

## References
- http://fortune.com/2019/02/05/zcash-vulnerability-cryptocurrency/
- https://z.cash/blog/zcash-counterfeiting-vulnerability-successfully-remediated/
- https://github.com/JinBean/CVE-Extension
