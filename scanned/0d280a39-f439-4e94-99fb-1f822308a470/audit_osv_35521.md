# [H] MosaicML Composer Deserialization of Untrusted Data Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-10043
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-10043
Type: osv

## Details
MosaicML Composer Deserialization of Untrusted Data Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of MosaicML Composer. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of checkpoints. The issue results from the lack of proper validation of user-supplied data, which can result in deserialization of untrusted data. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-27990.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10043.json
- https://github.com/mosaicml/composer/commit/6405188805a0054b4551ec49e4919c54c971d0e8
- https://nvd.nist.gov/vuln/detail/CVE-2026-10043
- https://www.zerodayinitiative.com/advisories/ZDI-26-384/
