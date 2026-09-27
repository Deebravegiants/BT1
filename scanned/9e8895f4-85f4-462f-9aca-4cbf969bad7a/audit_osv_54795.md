# [H] CVE-2024-4227

## Summary
Severity: High
Advisory: CVE-2024-4227
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-4227
Type: osv

## Details
In Genivia gSOAP with a specific configuration an unauthenticated remote attacker can generate a high CPU load when forcing to parse an XML having duplicate ID attributes which can lead to a DoS.

## References
- https://www.genivia.com/advisory.html#Upgrade_recommendation_when_option_-c++11_is_used_to_generate_C++11_source_code
- https://sourceforge.net/p/gsoap2/code/HEAD/tree/changelog.md
