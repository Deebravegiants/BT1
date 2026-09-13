# [H] CVE-2019-18213

## Summary
Severity: High
Advisory: CVE-2019-18213
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-23
Source: https://osv.dev/vulnerability/CVE-2019-18213
Type: osv

## Details
XML Language Server (aka lsp4xml) before 0.9.1, as used in Red Hat XML Language Support (aka vscode-xml) before 0.9.1 for Visual Studio and other products, allows XXE via a crafted XML document, with resultant SSRF (as well as SMB connection initiation that can lead to NetNTLM challenge/response capture for password cracking). This occurs in extensions/contentmodel/participants/diagnostics/LSPXMLParserConfiguration.java.

## References
- https://github.com/angelozerr/lsp4xml/
- https://github.com/angelozerr/lsp4xml/blob/master/CHANGELOG.md#others
- https://marketplace.visualstudio.com/items?itemName=redhat.vscode-xml
- https://github.com/angelozerr/lsp4xml/pull/566
- https://github.com/redhat-developer/vscode-xml/
- https://www.shielder.it/blog/dont-open-that-xml-xxe-to-rce-in-xml-plugins-for-vs-code-eclipse-theia/
