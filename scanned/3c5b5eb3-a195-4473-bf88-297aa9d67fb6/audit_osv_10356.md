# [M] CVE-2017-15094

## Summary
Severity: Medium
Advisory: CVE-2017-15094
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-15094
Type: osv

## Details
An issue has been found in the DNSSEC parsing code of PowerDNS Recursor from 4.0.0 up to and including 4.0.6 leading to a memory leak when parsing specially crafted DNSSEC ECDSA keys. These keys are only parsed when validation is enabled by setting dnssec to a value other than off or process-no-validate (default).

## References
- http://www.securityfocus.com/bid/101982
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2017-07.html
