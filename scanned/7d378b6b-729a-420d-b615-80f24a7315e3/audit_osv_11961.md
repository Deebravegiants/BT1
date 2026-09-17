# [H] CVE-2018-1000216

## Summary
Severity: High
Advisory: CVE-2018-1000216
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000216
Type: osv

## Details
Dave Gamble cJSON version 1.7.2 and earlier contains a CWE-415: Double Free vulnerability in cJSON library that can result in Possible crash or RCE. This attack appear to be exploitable via Attacker must be able to force victim to print JSON data, depending on how cJSON library is used this could be either local or over a network. This vulnerability appears to have been fixed in 1.7.3.

## References
- https://github.com/DaveGamble/cJSON/issues/241
