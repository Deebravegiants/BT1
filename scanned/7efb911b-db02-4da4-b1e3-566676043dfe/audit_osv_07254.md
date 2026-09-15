# [H] BIT-passenger-2025-26803

## Summary
Severity: High
Advisory: BIT-passenger-2025-26803
Aliases: BIT-passenger-apache-module-2025-26803, BIT-passenger-nginx-module-2025-26803, CVE-2025-26803, GHSA-2cj2-qqxj-5m3r
Ecosystem: Bitnami
Published: 2025-03-02
Source: https://osv.dev/vulnerability/BIT-passenger-2025-26803
Type: osv

## Affected
- Bitnami: `passenger` — affected >=6.0.21 <6.0.26

## Details
The http parser in Phusion Passenger 6.0.21 through 6.0.25 before 6.0.26 allows a denial of service during parsing of a request with an invalid HTTP method.

## References
- https://blog.phusion.nl/2025/02/19/passenger-6-0-26/
- https://github.com/phusion/passenger/commit/bb15591646687064ab2d578d5f9660b2a4168017
- https://github.com/phusion/passenger/compare/release-6.0.25...release-6.0.26
- https://github.com/phusion/passenger/releases/tag/release-6.0.26
- https://www.phusionpassenger.com/support
- https://nvd.nist.gov/vuln/detail/CVE-2025-26803
