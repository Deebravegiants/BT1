# [M] CVE-2020-8940

## Summary
Severity: Medium
Advisory: CVE-2020-8940
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8940
Type: osv

## Details
An arbitrary memory read vulnerability in Asylo versions up to 0.6.0 allows an untrusted attacker to make a call to enc_untrusted_recvmsg using an attacker controlled result parameter. The parameter size is unchecked allowing the attacker to read memory locations outside of the intended buffer size including memory addresses within the secure enclave. We recommend upgrading or past commit fa6485c5d16a7355eab047d4a44345a73bc9131e

## References
- https://github.com/google/asylo/commit/fa6485c5d16a7355eab047d4a44345a73bc9131e
