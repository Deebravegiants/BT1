# [M] JumpServer has a Server-Side Template Injection Leading to RCE via YAML Rendering

## Summary
Severity: Medium
Advisory: CVE-2026-31864
Aliases: GHSA-qx8h-rx2j-j5wc
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31864
Type: osv

## Details
JumpServer is an open source bastion host and an operation and maintenance security audit system. a Server-Side Template Injection (SSTI) vulnerability exists in JumpServer's Applet and VirtualApp upload functionality. This vulnerability can only be exploited by users with administrative privileges (Application Applet Management or Virtual Application Management permissions). Attackers can exploit this vulnerability to execute arbitrary code within the JumpServer Core container. The vulnerability arises from unsafe use of Jinja2 template rendering when processing user-uploaded YAML configuration files. When a user uploads an Applet or VirtualApp ZIP package, the manifest.yml file is rendered through Jinja2 without sandbox restrictions, allowing template injection attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31864.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-qx8h-rx2j-j5wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-31864
- https://github.com/jumpserver/jumpserver/pull/16608
