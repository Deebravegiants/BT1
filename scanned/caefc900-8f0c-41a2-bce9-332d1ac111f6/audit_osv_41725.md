# [M] o6 Automation open62541 Integer Overflow or Wraparound

## Summary
Severity: Medium
Advisory: CVE-2026-63559
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-63559
Type: osv

## Details
An integer overflow in the UA_Variant arrayDimensions product 
computation in open62541 may allow a remote attacker to read 
out-of-bounds heap memory, potentially disclosing sensitive information.

## References
- https://github.com/cisagov/CSAF/blob/develop/csaf_files/OT/white/2026/icsa-26-211-08.json
- https://github.com/open62541/open62541/pull/8235/commits/b666d35769ce63998442e4d0810a3fb10b50179f
- https://github.com/open62541/open62541/pull/8236/commits/06b99fef667c8ec5bdf0605b4f00c84fcc1d3a60
- https://github.com/open62541/open62541/pull/8237/commits/1b71d9c5d9c4d02d4729b8903a52e9f530bf804e
- https://github.com/open62541/open62541/pull/8238/commits/afab4107bfd161da9ce8bb30ed77f3968c9c97df
- https://www.o6-automation.com/contact
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63559.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63559
- https://www.cisa.gov/news-events/ics-advisories/icsa-26-211-08
