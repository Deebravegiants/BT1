# [M] CVE-2021-23991

## Summary
Severity: Medium
Advisory: CVE-2021-23991
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-23991
Type: osv

## Details
If a Thunderbird user has previously imported Alice's OpenPGP key, and Alice has extended the validity period of her key, but Alice's updated key has not yet been imported, an attacker may send an email containing a crafted version of Alice's key with an invalid subkey, Thunderbird might subsequently attempt to use the invalid subkey, and will fail to send encrypted email to Alice. This vulnerability affects Thunderbird < 78.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1673240
