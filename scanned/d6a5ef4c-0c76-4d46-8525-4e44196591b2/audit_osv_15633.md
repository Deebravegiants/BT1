# [M] CVE-2019-18212

## Summary
Severity: Medium
Advisory: CVE-2019-18212
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-18212
Type: osv

## Details
XMLLanguageService.java in XML Language Server (aka lsp4xml) before 0.9.1, as used in Red Hat XML Language Support (aka vscode-xml) before 0.9.1 for Visual Studio and other products, allows a remote attacker to write to arbitrary files via Directory Traversal.

## References
- https://github.com/angelozerr/lsp4xml/
- https://github.com/angelozerr/lsp4xml/blob/master/CHANGELOG.md#others
- https://marketplace.visualstudio.com/items?itemName=redhat.vscode-xml
- https://github.com/angelozerr/lsp4xml/pull/567
- https://github.com/redhat-developer/vscode-xml/
- https://www.shielder.it/blog/dont-open-that-xml-xxe-to-rce-in-xml-plugins-for-vs-code-eclipse-theia/
