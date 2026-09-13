# [H] Deserialization of untrusted data in MelisCms

## Summary
Severity: High
Advisory: CVE-2022-39297
Aliases: GHSA-m3m3-6gww-7gj9
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2022-10-12
Source: https://osv.dev/vulnerability/CVE-2022-39297
Type: osv

## Details
MelisCms provides a full CMS for Melis Platform, including templating system, drag'n'drop of plugins, SEO and many administration tools. Attackers can deserialize arbitrary data on affected versions of `melisplatform/melis-cms`, and ultimately leads to the execution of arbitrary PHP code on the system. Conducting this attack does not require authentication. Users should immediately upgrade to `melisplatform/melis-cms` >= 5.0.1. This issue was addressed by restricting allowed classes when deserializing user-controlled data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39297.json
- https://github.com/melisplatform/melis-cms/security/advisories/GHSA-m3m3-6gww-7gj9
- https://nvd.nist.gov/vuln/detail/CVE-2022-39297
- https://github.com/melisplatform/melis-cms/commit/d124b2474699a679a24ec52620cadceb3d4cec11
