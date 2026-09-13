# [M] CVE-2020-8941

## Summary
Severity: Medium
Advisory: CVE-2020-8941
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8941
Type: osv

## Details
An arbitrary memory read vulnerability in Asylo versions up to 0.6.0 allows an untrusted attacker to make a call to enc_untrusted_inet_pton using an attacker controlled klinux_addr_buffer parameter. The parameter size is unchecked allowing the attacker to read memory locations outside of the intended buffer size including memory addresses within the secure enclave. We recommend upgrading past commit 8fed5e334131abaf9c5e17307642fbf6ce4a57ec

## References
- https://github.com/google/asylo/commit/8fed5e334131abaf9c5e17307642fbf6ce4a57ec
