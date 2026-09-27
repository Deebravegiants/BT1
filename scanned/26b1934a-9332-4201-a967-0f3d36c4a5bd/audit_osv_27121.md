# [C] Arbitrary File Write in eosphoros-ai/db-gpt

## Summary
Severity: Critical
Advisory: CVE-2024-10834
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10834
Type: osv

## Details
eosphoros-ai/db-gpt version 0.6.0 contains a vulnerability in the RAG-knowledge endpoint that allows for arbitrary file write. The issue arises from the ability to pass an absolute path to a call to `os.path.join`, enabling an attacker to write files to arbitrary locations on the target server. This vulnerability can be exploited by setting the `doc_file.filename` to an absolute path, which can lead to overwriting system files or creating new SSH-key entries.

## References
- https://huntr.com/bounties/0d598508-151a-4050-9ccd-31bb82955e7a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10834.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10834
