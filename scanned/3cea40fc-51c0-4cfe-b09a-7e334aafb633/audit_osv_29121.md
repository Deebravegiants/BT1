# [H] Remote code execution in Haven IndieAuthClient (GHSL-2024-093)

## Summary
Severity: High
Advisory: CVE-2024-39906
Aliases: GHSA-65cm-7g24-hm9f
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-39906
Type: osv

## Details
A command injection vulnerability was found in the IndieAuth functionality of the Ruby on Rails based Haven blog web application. The affected functionality requires authentication, but an attacker can craft a link that they can pass to a logged in administrator of the blog software. This leads to the immediate execution of the provided commands when the link is accessed by the authenticated administrator. This issue may lead to Remote Code Execution (RCE) and has been addressed by commit `c52f07c`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39906.json
- https://github.com/havenweb/haven/security/advisories/GHSA-65cm-7g24-hm9f
- https://nvd.nist.gov/vuln/detail/CVE-2024-39906
- https://github.com/havenweb/haven/commit/c52f07c
