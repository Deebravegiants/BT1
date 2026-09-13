# [H] CVE-2020-22781

## Summary
Severity: High
Advisory: CVE-2020-22781
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-28
Source: https://osv.dev/vulnerability/CVE-2020-22781
Type: osv

## Details
In Etherpad < 1.8.3, a specially crafted URI would raise an unhandled exception in the cache mechanism and cause a denial of service (crash the instance).

## References
- https://github.com/ether/etherpad-lite/issues/3502
