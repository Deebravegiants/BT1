# [H] Tencent HunyuanVideo load_vae Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2025-13710
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-13710
Type: osv

## Details
Tencent HunyuanVideo load_vae Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Tencent HunyuanVideo. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the load_vae function.The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of root. Was ZDI-CAN-27186.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13710.json
- https://github.com/Tencent-Hunyuan/HunyuanVideo/commit/b47e10b95483aa8458b64d23350844c29e91c408
- https://nvd.nist.gov/vuln/detail/CVE-2025-13710
- https://www.zerodayinitiative.com/advisories/ZDI-25-1030/
