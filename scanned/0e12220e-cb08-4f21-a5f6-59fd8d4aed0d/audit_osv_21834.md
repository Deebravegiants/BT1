# [M] CVE-2021-47713

## Summary
Severity: Medium
Advisory: CVE-2021-47713
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-12-22
Source: https://osv.dev/vulnerability/CVE-2021-47713
Type: osv

## Details
Hasura GraphQL 1.3.3 contains a denial of service vulnerability that allows attackers to overwhelm the service by crafting malicious GraphQL queries with excessive nested fields. Attackers can send repeated requests with extremely long query strings and multiple threads to consume server resources and potentially crash the GraphQL endpoint.

## References
- https://github.com/hasura/graphql-engine
- https://www.exploit-db.com/exploits/49789
- https://www.vulncheck.com/advisories/hasura-graphql-denial-of-service-via-malicious-graphql-query
