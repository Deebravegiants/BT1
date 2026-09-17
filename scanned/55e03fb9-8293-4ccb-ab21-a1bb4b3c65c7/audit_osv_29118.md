# [M] OpenSearch Observability does not properly restrict access to private tenant resources

## Summary
Severity: Medium
Advisory: CVE-2024-39901
Aliases: GHSA-77vc-rj32-2r33
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-39901
Type: osv

## Details
OpenSearch Observability is collection of plugins and applications that visualize data-driven events. An issue in the OpenSearch observability plugins allows unintended access to private tenant resources like notebooks. The system did not properly check if the user was the resource author when accessing resources in a private tenant, leading to potential data being revealed. The patches are included in OpenSearch 2.14.

## References
- https://opensearch.org/versions/opensearch-2-14-0.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39901.json
- https://github.com/opensearch-project/observability/security/advisories/GHSA-77vc-rj32-2r33
- https://nvd.nist.gov/vuln/detail/CVE-2024-39901
- https://github.com/opensearch-project/observability/commit/014423178f8f61d90442dde03cbdcd754c70a84e
