# [H] GPT Academic stream_daas Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-0762
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-0762
Type: osv

## Details
GPT Academic stream_daas Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GPT Academic. Interaction with a malicious DAAS server is required to exploit this vulnerability but attack vectors may vary depending on the implementation.

The specific flaw exists within the stream_daas function. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-27956.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0762.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0762
- https://www.zerodayinitiative.com/advisories/ZDI-26-028/
