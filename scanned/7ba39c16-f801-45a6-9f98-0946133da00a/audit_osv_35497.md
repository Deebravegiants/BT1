# [C] Foundation Agents MetaGPT deserialize_message Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-0760
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0760
Type: osv

## Details
Foundation Agents MetaGPT deserialize_message Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Foundation Agents MetaGPT. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the deserialize_message function. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-28121.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0760.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0760
- https://www.zerodayinitiative.com/advisories/ZDI-26-026/
