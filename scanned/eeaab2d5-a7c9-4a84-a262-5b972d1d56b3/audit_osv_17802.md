# [H] CVE-2020-19861

## Summary
Severity: High
Advisory: CVE-2020-19861
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2020-19861
Type: osv

## Details
When a zone file in ldns 1.7.1 is parsed, the function ldns_nsec3_salt_data is too trusted for the length value obtained from the zone file. When the memcpy is copied, the 0xfe - ldns_rdf_size(salt_rdf) byte data can be copied, causing heap overflow information leakage.

## References
- https://cwe.mitre.org/data/definitions/126.html
- https://github.com/NLnetLabs/ldns/issues/51
