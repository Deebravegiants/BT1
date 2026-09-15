# [H] Aeon load_rehab_pile_dataset Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-18285
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-18285
Type: osv

## Details
Aeon load_rehab_pile_dataset Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Aeon. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the load_rehab_pile_dataset method. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28749.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18285.json
- https://github.com/aeon-toolkit/aeon/commit/751918052c0cce266b4f7cd4b084408526efc015
- https://nvd.nist.gov/vuln/detail/CVE-2026-18285
- https://www.zerodayinitiative.com/advisories/ZDI-26-468/
