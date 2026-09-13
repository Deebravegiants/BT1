# [H] libxmljs2 namespaces type confusion RCE

## Summary
Severity: High
Advisory: CVE-2024-34394
Aliases: GHSA-78h3-pg4x-j8cv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-02
Source: https://osv.dev/vulnerability/CVE-2024-34394
Type: osv

## Details
libxmljs2 is vulnerable to a type confusion vulnerability when parsing a specially crafted XML while invoking the namespaces() function (which invokes XmlNode::get_local_namespaces()) on a grand-child of a node that refers to an entity. This vulnerability can lead to denial of service and remote code execution.

## References
- https://research.jfrog.com/vulnerabilities/libxmljs2-namespaces-type-confusion-rce-jfsa-2024-001034098/
- https://www.npmjs.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34394
- https://github.com/marudor/libxmljs2/issues/205
