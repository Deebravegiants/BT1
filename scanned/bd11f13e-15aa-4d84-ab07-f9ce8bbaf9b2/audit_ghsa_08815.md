# [H] Electerm Security Vulnerability: RCE via malicious SSH server filename in openFileWithEditor

## Summary
Severity: High
Advisory: GHSA-q4p8-8j9m-8hxj
CVE: CVE-2026-43943
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-q4p8-8j9m-8hxj
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.7.9

## Details
### Impact

A code execution (RCE) vulnerability exists in electerm's SFTP open with system editor or "Edit with custom editor" feature. When a user opts to edit a file using open with system editor or open with a custom editor, the filename is passed directly into a command line without sanitization.

A malicious actor controlling the SSH server or user OS can exploit this by crafting a filename containing shell metacharacters. If a victim subsequently attempts to edit this file, the injected commands are executed on their machine with the user's privileges. This could allow the attacker to run arbitrary code, install malware, or move laterally within the network.

<img width="1792" height="817" alt="1" src="https://github.com/user-attachments/assets/ddf78890-e95d-4fe7-981e-f86887677e8b" />
<img width="1648" height="941" alt="2" src="https://github.com/user-attachments/assets/cca2295b-2053-4d99-a464-be51eac2f5be" />

### Patches

Fixed in version >= 3.7.9

- https://github.com/electerm/electerm/commit/24ce7103e264cffe6eb5476c0506a2379e6f8333

### Workarounds

Until a patch is available, it is strongly recommended to:  
- Refrain from using the open with system editor  or "Edit with custom editor" feature when connected to untrusted or unfamiliar SSH servers.  
- Consider using the built-in editor for viewing files, as this path may not be vulnerable to the same injection.  
- If the feature must be used, ensure connections are exclusively established with trusted servers and perform rigorous filename validation before editing.

### Resources

- [electerm GitHub Repository](https://github.com/electerm/electerm)

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-q4p8-8j9m-8hxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-43943
- https://github.com/electerm/electerm/commit/24ce7103e264cffe6eb5476c0506a2379e6f8333
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.7.9
