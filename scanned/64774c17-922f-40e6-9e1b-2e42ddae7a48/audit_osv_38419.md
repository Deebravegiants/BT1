# [C] OpenEMR 8.2.0 Remote Code Execution via CategoryTree eval() Injection

## Summary
Severity: Critical
Advisory: CVE-2026-39932
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-39932
Type: osv

## Details
OpenEMR through 8.2.0 contains a remote code execution vulnerability in the document category tree component (library/classes/Tree.class.php) that allows authenticated administrators to execute arbitrary operating system commands by injecting PHP payloads into the categories database table. Attackers can chain arbitrary SQL execution to alter the id column type to VARCHAR and insert a malicious PHP payload, which is then executed via an unsanitized eval() call whenever any page instantiates CategoryTree, including unauthenticated and low-privilege pages, resulting in command execution as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39932.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39932
- https://www.vulncheck.com/advisories/openemr-remote-code-execution-via-categorytree-eval-injection
- https://github.com/openemr/openemr
- https://jivasecurity.com/writeups/openemr-eval-rce-category-tree-cve-2026-39932
