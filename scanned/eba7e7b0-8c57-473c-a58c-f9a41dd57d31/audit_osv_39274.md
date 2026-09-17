# [H] libzypp path traversal via "keyhint" in repomd.xml

## Summary
Severity: High
Advisory: CVE-2026-44941
CVSS: 8.4 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-44941
Type: osv

## Details
A relative path traversal in the "keyhint" option in repomd.xml parsing of libzypp before 17.38.12 can be used by attackers able to supply a malicious repository to inject or overwrite files in the target system as root.

## References
- https://github.com/openSUSE/libzypp/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44941.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-44941
- https://bugzilla.suse.com/show_bug.cgi?id=1267426
- https://github.com/openSUSE/libzypp/commit/294b1bad442d089ca671c5c03adc8031e3b29e04
