# [C] CVE-2018-1000217

## Summary
Severity: Critical
Advisory: CVE-2018-1000217
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000217
Type: osv

## Details
Dave Gamble cJSON version 1.7.3 and earlier contains a CWE-416: Use After Free vulnerability in cJSON library that can result in Possible crash, corruption of data or even RCE. This attack appear to be exploitable via Depends on how application uses cJSON library. If application provides network interface then can be exploited over a network, otherwise just local.. This vulnerability appears to have been fixed in 1.7.4.

## References
- https://github.com/DaveGamble/cJSON/issues/248
