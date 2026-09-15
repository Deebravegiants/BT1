# [H] CVE-2018-6480

## Summary
Severity: High
Advisory: CVE-2018-6480
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2018-6480
Type: osv

## Details
A type confusion issue was discovered in CCN-lite 2, leading to a memory access violation and a failure of the nonce feature (which, for example, helped with loop prevention). ccnl_fwd_handleInterest assumes that the union member s is of type ccnl_pktdetail_ndntlv_s. However, if the type is in fact struct ccnl_pktdetail_ccntlv_s or struct ccnl_pktdetail_iottlv_s, the memory at that point is either uninitialised or points to data that is not a nonce, which renders the code using the local variable nonce pointless. A later nonce check is insufficient.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/159
