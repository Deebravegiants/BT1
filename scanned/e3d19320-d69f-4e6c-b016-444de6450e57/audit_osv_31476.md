# [C] oobabooga text-generation-webui trust_remote_code Reliance on Untrusted Inputs Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2025-12487
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2025-12487
Type: osv

## Details
oobabooga text-generation-webui trust_remote_code Reliance on Untrusted Inputs Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of oobabooga text-generation-webui. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of the trust_remote_code parameter provided to the join endpoint. The issue results from the lack of proper validation of a user-supplied argument before using it to load a model. An attacker can leverage this vulnerability to execute code in the context of the service account. Was ZDI-CAN-26681.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12487.json
- https://github.com/oobabooga/text-generation-webui/commit/b5a6904c4ac4049823396090360b6f566f4e4603
- https://nvd.nist.gov/vuln/detail/CVE-2025-12487
- https://www.zerodayinitiative.com/advisories/ZDI-25-982/
