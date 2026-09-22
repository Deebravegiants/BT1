# [C] xmldom allows multiple root nodes in a DOM

## Summary
Severity: Critical
Advisory: GHSA-crh6-fp67-6883
CVE: CVE-2022-39353
CWE: CWE-1288, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-crh6-fp67-6883
Type: github-advisory

## Affected
- npm: `xmldom` — affected >=0
- npm: `@xmldom/xmldom` — affected >=0 <0.7.7
- npm: `@xmldom/xmldom` — affected >=0.8.0 <0.8.4
- npm: `@xmldom/xmldom` — affected >=0.9.0-beta.1 <0.9.0-beta.4

## Details
### Impact
xmldom parses XML that is not well-formed because it contains multiple top level elements, and adds all root nodes to the `childNodes` collection of the `Document`, without reporting any error or throwing.
This breaks the assumption that there is only a single root node in the tree, which led to https://nvd.nist.gov/vuln/detail/CVE-2022-39299 and is a potential issue for dependents.

### Patches
Update to `@xmldom/xmldom@~0.7.7`, `@xmldom/xmldom@~0.8.4` (dist-tag `latest`) or `@xmldom/xmldom@>=0.9.0-beta.4` (dist-tag `next`).

### Workarounds
One of the following approaches might help, depending on your use case:
- Instead of searching for elements in the whole DOM, only search in the `documentElement`.
- Reject a document with a document that has more then 1 `childNode`.

### References
- https://nvd.nist.gov/vuln/detail/CVE-2022-39299
- https://github.com/jindw/xmldom/issues/150

### For more information
If you have any questions or comments about this advisory:
* Email us at security@xmldom.org

## References
- https://github.com/xmldom/xmldom/security/advisories/GHSA-crh6-fp67-6883
- https://nvd.nist.gov/vuln/detail/CVE-2022-39353
- https://github.com/jindw/xmldom/issues/150
- https://github.com/xmldom/xmldom/commit/52a708360c35aa160fcca8621720d71fd0f95f1a
- https://github.com/xmldom/xmldom/commit/7ff7c10ab2961703ac1752e95b4ff60ee4ee6643
- https://github.com/xmldom/xmldom/commit/c02f786216bed70825f9a351c65e61500f51e931
- https://github.com/xmldom/xmldom
- https://github.com/xmldom/xmldom/releases/tag/0.7.7
- https://github.com/xmldom/xmldom/releases/tag/0.8.4
- https://github.com/xmldom/xmldom/releases/tag/0.9.0-beta.4
- https://lists.debian.org/debian-lts-announce/2023/01/msg00000.html
