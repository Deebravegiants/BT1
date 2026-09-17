# [H] Microsoft.OpenApi.YamlReader/Readers vulnerable to denial of service via YAML alias expansion

## Summary
Severity: High
Advisory: CVE-2026-72923
Aliases: GHSA-7pxr-59rr-hqj2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-72923
Type: osv

## Details
In Microsoft.OpenApi.YamlReader from 2.0.0-preview.11 until 2.12.0 and from 3.0.0 until 3.10.0, and in Microsoft.OpenApi.Readers prior to 1.6.30, a small YAML OpenAPI document containing nested anchors and aliases can cause uncontrolled resource consumption when parsed through the public YAML reader APIs. YAML is parsed through SharpYaml, which represents aliases as shared nodes in a directed acyclic graph, so the parsed YAML graph stays small, but converting that graph to System.Text.Json.Nodes.JsonNode requires every alias to be materialized as an independent node because a JsonNode cannot be attached to multiple parents. Without a bound on that conversion work, a document with N nested anchors each referenced k times can require k^N materialized JSON nodes, leading to excessive memory allocation and process termination through out-of-memory conditions, a billion laughs style denial of service. The patched versions bound the YAML-to-JSON conversion by node count and nesting depth and report an OpenApiDiagnostic error instead of expanding without limit. This vulnerability is fixed in Microsoft.OpenApi.YamlReader 2.12.0 and 3.10.0, and Microsoft.OpenApi.Readers 1.6.30.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72923.json
- https://github.com/microsoft/OpenAPI.NET/security/advisories/GHSA-7pxr-59rr-hqj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-72923
