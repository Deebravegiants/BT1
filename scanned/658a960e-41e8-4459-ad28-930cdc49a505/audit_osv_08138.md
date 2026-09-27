# [H] CVE-2016-10568

## Summary
Severity: High
Advisory: CVE-2016-10568
Aliases: GHSA-ff29-f57w-2mm3
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-29
Source: https://osv.dev/vulnerability/CVE-2016-10568
Type: osv

## Details
geoip-lite-country is a stripped down version of geoip-lite, supporting only country lookup. geoip-lite-country before 1.1.4 downloads data resources over HTTP, which leaves it vulnerable to MITM attacks.

## References
- https://nodesecurity.io/advisories/183
