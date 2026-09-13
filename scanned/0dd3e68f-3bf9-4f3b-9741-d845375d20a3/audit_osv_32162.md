# [H] GPT Academic allows arbitary file read by tarfile uncompress within softlink

## Summary
Severity: High
Advisory: CVE-2025-25185
Aliases: GHSA-gqp5-wm97-qxcv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-25185
Type: osv

## Details
GPT Academic provides interactive interfaces for large language models. In 3.91 and earlier, GPT Academic does not properly account for soft links. An attacker can create a malicious file as a soft link pointing to a target file, then package this soft link file into a tar.gz file and upload it. Subsequently, when accessing the decompressed file from the server, the soft link will point to the target file on the victim server. The vulnerability allows attackers to read all files on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25185.json
- https://github.com/binary-husky/gpt_academic/security/advisories/GHSA-gqp5-wm97-qxcv
- https://nvd.nist.gov/vuln/detail/CVE-2025-25185
- https://github.com/binary-husky/gpt_academic/commit/5dffe8627f681d7006cebcba27def038bb691949
