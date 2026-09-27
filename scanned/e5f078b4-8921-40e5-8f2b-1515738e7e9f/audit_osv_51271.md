# [M] CVE-2021-23993

## Summary
Severity: Medium
Advisory: CVE-2021-23993
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-23993
Type: osv

## Details
An attacker may perform a DoS attack to prevent a user from sending encrypted email to a correspondent. If an attacker creates a crafted OpenPGP key with a subkey that has an invalid self signature, and the Thunderbird user imports the crafted key, then Thunderbird may try to use the invalid subkey, but the RNP library rejects it from being used, causing encryption to fail. This vulnerability affects Thunderbird < 78.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1666360
