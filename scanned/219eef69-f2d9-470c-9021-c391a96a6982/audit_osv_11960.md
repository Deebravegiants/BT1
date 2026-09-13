# [H] CVE-2018-1000215

## Summary
Severity: High
Advisory: CVE-2018-1000215
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000215
Type: osv

## Details
Dave Gamble cJSON version 1.7.6 and earlier contains a CWE-772 vulnerability in cJSON library that can result in Denial of Service (DoS). This attack appear to be exploitable via If the attacker can force the data to be printed and the system is in low memory it can force a leak of memory. This vulnerability appears to have been fixed in 1.7.7.

## References
- https://github.com/DaveGamble/cJSON/issues/267
