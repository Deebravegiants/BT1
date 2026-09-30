# [M] CVE-2020-8905

## Summary
Severity: Medium
Advisory: CVE-2020-8905
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-12
Source: https://osv.dev/vulnerability/CVE-2020-8905
Type: osv

## Details
A buffer length validation vulnerability in Asylo versions prior to 0.6.0 allows an attacker to read data they should not have access to. The 'enc_untrusted_recvfrom' function generates a return value which is deserialized by 'MessageReader', and copied into three different 'extents'. The length of the third 'extents' is controlled by the outside world, and not verified on copy, allowing the attacker to force Asylo to copy trusted memory data into an untrusted buffer of significantly small length.. We recommend updating Asylo to version 0.6.0 or later.

## References
- https://github.com/google/asylo/commit/299f804acbb95a612ab7c504d25ab908aa59ae93
