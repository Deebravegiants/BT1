# [M] CVE-2018-20587

## Summary
Severity: Medium
Advisory: CVE-2018-20587
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-02-11
Source: https://osv.dev/vulnerability/CVE-2018-20587
Type: osv

## Details
Bitcoin Core 0.12.0 through 0.17.1 and Bitcoin Knots 0.12.0 through 0.17.x before 0.17.1.knots20181229 have Incorrect Access Control. Local users can exploit this to steal currency by binding the RPC IPv4 localhost port, and forwarding requests to the IPv6 localhost port.

## References
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures#CVE-2018-20587
- https://medium.com/%40lukedashjr/cve-2018-20587-advisory-and-full-disclosure-a3105551e78b
