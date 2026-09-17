# [H] Partial rule set bypass in OWASP ModSecurity Core Rule Set  for HTTP multipart requests using  character encoding in the Content-Type or Content-Transfer-Encoding header

## Summary
Severity: High
Advisory: CVE-2022-39956
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-09-20
Source: https://osv.dev/vulnerability/CVE-2022-39956
Type: osv

## Details
The OWASP ModSecurity Core Rule Set (CRS) is affected by a partial rule set bypass for HTTP multipart requests by submitting a payload that uses a character encoding scheme via the Content-Type or the deprecated Content-Transfer-Encoding multipart MIME header fields that will not be decoded and inspected by the web application firewall engine and the rule set. The multipart payload will therefore bypass detection. A vulnerable backend that supports these encoding schemes can potentially be exploited. The legacy CRS versions 3.0.x and 3.1.x are affected, as well as the currently supported versions 3.2.1 and 3.3.2. Integrators and users are advised upgrade to 3.2.2 and 3.3.3 respectively. The mitigation against these vulnerabilities depends on the installation of the latest ModSecurity version (v2.9.6 / v3.0.8).

## References
- https://coreruleset.org/20220919/crs-version-3-3-3-and-3-2-2-covering-several-cves/
- https://lists.debian.org/debian-lts-announce/2025/08/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39956.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HL2L2GF7GOCWPMJZDUE5OXDSXHGG3XUJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PD56EAYNGB6E6QQH62LAYCONOP6OH5DZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPQ6CCMX3MU4A7MTCGQJA7VMJW3IQDXV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39956
- https://security.gentoo.org/glsa/202305-25
- https://lists.debian.org/debian-lts-announce/2023/01/msg00033.html
