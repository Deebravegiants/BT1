# [M] CVE-2021-23992

## Summary
Severity: Medium
Advisory: CVE-2021-23992
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-06-24
Source: https://osv.dev/vulnerability/CVE-2021-23992
Type: osv

## Details
Thunderbird did not check if the user ID associated with an OpenPGP key has a valid self signature. An attacker may create a crafted version of an OpenPGP key, by either replacing the original user ID, or by adding another user ID. If Thunderbird imports and accepts the crafted key, the Thunderbird user may falsely conclude that the false user ID belongs to the correspondent. This vulnerability affects Thunderbird < 78.9.1.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1666236
