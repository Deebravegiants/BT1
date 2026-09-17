# [H] Apache Batik prior to 1.16 allows RCE when loading untrusted SVG input

## Summary
Severity: High
Advisory: CVE-2022-41704
Aliases: GHSA-r29w-r9ph-vm76
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-10-25
Source: https://osv.dev/vulnerability/CVE-2022-41704
Type: osv

## Details
A vulnerability in Batik of Apache XML Graphics allows an attacker to run untrusted Java code from an SVG. This issue affects Apache XML Graphics prior to 1.16. It is recommended to update to version 1.16.

## References
- https://lists.apache.org/thread/hplhx0o74jb7blj39fm4kw3otcnjd6xf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41704.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41704
- https://security.gentoo.org/glsa/202401-11
- https://www.debian.org/security/2022/dsa-5264
- http://www.openwall.com/lists/oss-security/2022/10/25/2
- https://lists.debian.org/debian-lts-announce/2022/10/msg00038.html
