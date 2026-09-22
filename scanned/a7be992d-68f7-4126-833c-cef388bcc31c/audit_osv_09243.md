# [C] CVE-2016-9132

## Summary
Severity: Critical
Advisory: CVE-2016-9132
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2016-9132
Type: osv

## Details
In Botan 1.8.0 through 1.11.33, when decoding BER data an integer overflow could occur, which would cause an incorrect length field to be computed. Some API callers may use the returned (incorrect and attacker controlled) length field in a way which later causes memory corruption or other failure.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4OUDGVRQYQUL7F5MRP3LAV7EHRJG4BBE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z2Y3JLMTE3VIV4X5X6SXVZTJBDDLCS3D/
- http://www.securityfocus.com/bid/95879
- https://github.com/randombit/botan/commit/987ad747db6d0d7e36f840398f3cf02e2fbfd90f
