# [C] CVE-2017-8045

## Summary
Severity: Critical
Advisory: CVE-2017-8045
Aliases: GHSA-vqqg-xgv7-cf68
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-8045
Type: osv

## Details
In Pivotal Spring AMQP versions prior to 1.7.4, 1.6.11, and 1.5.7, an org.springframework.amqp.core.Message may be unsafely deserialized when being converted into a string. A malicious payload could be crafted to exploit this and enable a remote code execution attack.

## References
- http://www.securityfocus.com/bid/100936
- https://pivotal.io/security/cve-2017-8045
