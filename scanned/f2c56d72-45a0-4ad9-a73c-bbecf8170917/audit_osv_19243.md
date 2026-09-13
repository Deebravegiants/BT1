# [M] CVE-2020-8942

## Summary
Severity: Medium
Advisory: CVE-2020-8942
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8942
Type: osv

## Details
An arbitrary memory read vulnerability in Asylo versions up to 0.6.0 allows an untrusted attacker to make a call to enc_untrusted_read whose return size was not validated against the requrested size. The parameter size is unchecked allowing the attacker to read memory locations outside of the intended buffer size including memory addresses within the secure enclave. We recommend upgrading past commit b1d120a2c7d7446d2cc58d517e20a1b184b82200

## References
- https://github.com/google/asylo/commit/b1d120a2c7d7446d2cc58d517e20a1b184b82200
