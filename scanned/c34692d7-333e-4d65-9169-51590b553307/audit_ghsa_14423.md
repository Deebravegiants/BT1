# [H] Stud42 vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-3hwm-922r-47hw
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-3hwm-922r-47hw
Type: github-advisory

## Affected
- Go: `atomys.codes/stud42` — affected >=0 <0.23.0

## Details
A security vulnerability has been identified in the GraphQL parser used by the API of s42.app. An attacker can overload the parser and cause the API pod to crash. With a bit of threading, the attacker can bring down the entire API, resulting in an unhealthy stream. This vulnerability can be exploited by sending a specially crafted request to the API with a large payload.

An attacker can exploit this vulnerability to cause a denial of service (DoS) attack on the s42.app API, resulting in unavailability of the API for legitimate users.

## References
- https://github.com/42Atomys/stud42/security/advisories/GHSA-3hwm-922r-47hw
- https://github.com/42Atomys/stud42/issues/412
- https://github.com/42Atomys/stud42/commit/a70bfc72fba721917bf681d72a58093fb9deee17
- https://github.com/42Atomys/stud42
