# [H] CVE-2020-16881

## Summary
Severity: High
Advisory: CVE-2020-16881
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2020-16881
Type: osv

## Details
<p>A remote code execution vulnerability exists in Visual Studio Code when a user is tricked into opening a malicious 'package.json' file. An attacker who successfully exploited the vulnerability could run arbitrary code in the context of the current user. If the current user is logged on with administrative user rights, an attacker could take control of the affected system. An attacker could then install programs; view, change, or delete data; or create new accounts with full user rights.</p>
<p>To exploit this vulnerability, an attacker would need to convince a target to clone a repository and open it in Visual Studio Code. Attacker-specified code would execute when the target opens the malicious 'package.json' file.</p>
<p>The update address the vulnerability by modifying the way Visual Studio Code handles JSON files.</p>

## References
- https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-16881
