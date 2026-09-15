# [H] CVE-2016-7966

## Summary
Severity: High
Advisory: CVE-2016-7966
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-7966
Type: osv

## Details
Through a malicious URL that contained a quote character it was possible to inject HTML code in KMail's plaintext viewer. Due to the parser used on the URL it was not possible to include the equal sign (=) or a space into the injected HTML, which greatly reduces the available HTML functionality. Although it is possible to include an HTML comment indicator to hide content.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QNMM5TVPTJQFPJ3YDF4DPXDFW3GQLWLY/
- http://www.debian.org/security/2016/dsa-3697
- http://www.openwall.com/lists/oss-security/2016/10/05/1
- http://www.securityfocus.com/bid/93360
- http://lists.opensuse.org/opensuse-updates/2016-10/msg00065.html
