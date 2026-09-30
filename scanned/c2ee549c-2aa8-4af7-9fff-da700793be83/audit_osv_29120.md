# [H] Code Execution Vulnerability via Local File Path Traversal in Vnote

## Summary
Severity: High
Advisory: CVE-2024-39904
Aliases: GHSA-vhh5-8wcv-68gj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-39904
Type: osv

## Details
VNote is a note-taking platform. Prior to 3.18.1, a code execution vulnerability existed in VNote, which allowed an attacker to execute arbitrary programs on the victim's system. A crafted URI can be used in a note to perform this attack using file:/// as a link. For example, file:///C:/WINDOWS/system32/cmd.exe. This allows attackers to execute arbitrary programs by embedding a reference to a local executable file such as file:///C:/WINDOWS/system32/cmd.exe and file:///C:/WINDOWS/system32/calc.exe. This vulnerability can be exploited by creating and sharing specially crafted notes. An attacker could send a crafted note file and perform further attacks. This vulnerability is fixed in 3.18.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39904.json
- https://github.com/vnotex/vnote/security/advisories/GHSA-vhh5-8wcv-68gj
- https://nvd.nist.gov/vuln/detail/CVE-2024-39904
- https://github.com/vnotex/vnote/commit/3477469b669708ff547037fda9fc2817870428aa
