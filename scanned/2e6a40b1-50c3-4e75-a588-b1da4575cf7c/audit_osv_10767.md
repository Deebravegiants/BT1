# [H] CVE-2017-2299

## Summary
Severity: High
Advisory: CVE-2017-2299
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-15
Source: https://osv.dev/vulnerability/CVE-2017-2299
Type: osv

## Details
Versions of the puppetlabs-apache module prior to 1.11.1 and 2.1.0 make it very easy to accidentally misconfigure TLS trust. If you specify the `ssl_ca` parameter but do not specify the `ssl_certs_dir` parameter, a default will be provided for the `ssl_certs_dir` that will trust certificates from any of the system-trusted certificate authorities. This did not affect FreeBSD.

## References
- http://www.securityfocus.com/bid/100859
- https://puppet.com/security/cve/CVE-2017-2299
