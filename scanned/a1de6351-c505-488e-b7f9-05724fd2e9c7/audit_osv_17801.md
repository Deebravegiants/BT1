# [M] CVE-2020-19860

## Summary
Severity: Medium
Advisory: CVE-2020-19860
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2020-19860
Type: osv

## Details
When ldns version 1.7.1 verifies a zone file, the ldns_rr_new_frm_str_internal function has a heap out of bounds read vulnerability. An attacker can leak information on the heap by constructing a zone file payload.

## References
- https://github.com/NLnetLabs/ldns/issues/50
- https://github.com/NLnetLabs/ldns/commit/15d96206996bea969fbc918eb0a4a346f514b9f3
