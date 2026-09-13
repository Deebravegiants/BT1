# [H] Deserialization of Untrusted Data in binary-husky/gpt_academic

## Summary
Severity: High
Advisory: CVE-2024-11039
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11039
Type: osv

## Details
A pickle deserialization vulnerability exists in the Latex English error correction plug-in function of binary-husky/gpt_academic versions up to and including 3.83. This vulnerability allows attackers to achieve remote command execution by deserializing untrusted data. The issue arises from the inclusion of numpy in the deserialization whitelist, which can be exploited by constructing a malicious compressed package containing a merge_result.pkl file and a merge_proofread_en.tex file. The vulnerability is fixed in commit 91f5e6b.

## References
- https://huntr.com/bounties/f233a365-522c-44f6-876f-db492fb58ad5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11039.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11039
- https://github.com/binary-husky/gpt_academic/commit/91f5e6b8f754beb47b02f7c1893804c1c9543ccb
