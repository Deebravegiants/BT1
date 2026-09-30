# [H] Deserialization of untrusted data in DataHub

## Summary
Severity: High
Advisory: CVE-2023-25558
Aliases: GHSA-hrwp-2q5c-86wv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-25558
Type: osv

## Details
DataHub is an open-source metadata platform. When the DataHub frontend is configured to authenticate via SSO, it will leverage the pac4j library. The processing of the `id_token` is done in an unsafe manner which is not properly accounted for by the DataHub frontend. Specifically, if any of the id_token claims value start with the {#sb64} prefix, pac4j considers the value to be a serialized Java object and will deserialize it. This issue may lead to Remote Code Execution (RCE) in the worst case. Although a `RestrictedObjectInputStream` is in place, that puts some restriction on what classes can be deserialized, it still allows a broad range of java packages and potentially exploitable with different gadget chains. Users are advised to upgrade. There are no known workarounds. This vulnerability was discovered and reported by the GitHub Security lab and is tracked as GHSL-2022-086.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25558.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-hrwp-2q5c-86wv
- https://nvd.nist.gov/vuln/detail/CVE-2023-25558
- https://github.com/datahub-project/datahub/commit/2a182f484677d056730d6b4e9f0143e67368359f
