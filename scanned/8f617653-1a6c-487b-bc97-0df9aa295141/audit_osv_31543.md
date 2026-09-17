# [H] Zip Slip Vulnerability in nltk/nltk Leading to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2025-14009
Aliases: GHSA-7p94-766c-hgjp, PYSEC-2026-96
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-14009
Type: osv

## Details
A critical vulnerability exists in the NLTK downloader component of nltk/nltk, affecting all versions. The _unzip_iter function in nltk/downloader.py uses zipfile.extractall() without performing path validation or security checks. This allows attackers to craft malicious zip packages that, when downloaded and extracted by NLTK, can execute arbitrary code. The vulnerability arises because NLTK assumes all downloaded packages are trusted and extracts them without validation. If a malicious package contains Python files, such as __init__.py, these files are executed automatically upon import, leading to remote code execution. This issue can result in full system compromise, including file system access, network access, and potential persistence mechanisms.

## References
- https://huntr.com/bounties/49ecbc02-054e-4470-b2e0-b267936cc4e4
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-14009.json
- https://access.redhat.com/errata/RHSA-2026:10184
- https://access.redhat.com/security/cve/CVE-2025-14009
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14009.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14009
- https://bugzilla.redhat.com/show_bug.cgi?id=2440724
