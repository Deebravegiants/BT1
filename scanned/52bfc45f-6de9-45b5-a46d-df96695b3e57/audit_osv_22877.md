# [H] Response body bypass in OWASP ModSecurity Core Rule Set via repeated HTTP Range header submission with a small byte range

## Summary
Severity: High
Advisory: CVE-2022-39958
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-09-20
Source: https://osv.dev/vulnerability/CVE-2022-39958
Type: osv

## Details
The OWASP ModSecurity Core Rule Set (CRS) is affected by a response body bypass to sequentially exfiltrate small and undetectable sections of data by repeatedly submitting an HTTP Range header field with a small byte range. A restricted resource, access to which would ordinarily be detected, may be exfiltrated from the backend, despite being protected by a web application firewall that uses CRS. Short subsections of a restricted resource may bypass pattern matching techniques and allow undetected access. The legacy CRS versions 3.0.x and 3.1.x are affected, as well as the currently supported versions 3.2.1 and 3.3.2. Integrators and users are advised to upgrade to 3.2.2 and 3.3.3 respectively and to configure a CRS paranoia level of 3 or higher.

## References
- https://coreruleset.org/20220919/crs-version-3-3-3-and-3-2-2-covering-several-cves/
- https://lists.debian.org/debian-lts-announce/2025/08/msg00004.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39958.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HL2L2GF7GOCWPMJZDUE5OXDSXHGG3XUJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PD56EAYNGB6E6QQH62LAYCONOP6OH5DZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YPQ6CCMX3MU4A7MTCGQJA7VMJW3IQDXV/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39958
- https://security.gentoo.org/glsa/202305-25
- https://lists.debian.org/debian-lts-announce/2023/01/msg00033.html
