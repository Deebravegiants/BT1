# [H] CVE-2016-9036

## Summary
Severity: High
Advisory: CVE-2016-9036
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-9036
Type: osv

## Details
An exploitable incorrect return value vulnerability exists in the mp_check function of Tarantool's Msgpuck library 1.0.3. A specially crafted packet can cause the mp_check function to incorrectly return success when trying to check if decoding a map16 packet will read outside the bounds of a buffer, resulting in a denial of service vulnerability.

## References
- http://www.securityfocus.com/bid/95064
- http://www.talosintelligence.com/reports/TALOS-2016-0254/
