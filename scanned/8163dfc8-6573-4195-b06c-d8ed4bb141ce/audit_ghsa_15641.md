# [M] The OpenSearch reporting plugin improperly controls tenancy access to reporting resources

## Summary
Severity: Medium
Advisory: GHSA-xmvg-335g-x44q
CVE: CVE-2024-39900
CWE: CWE-639
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-18
Source: https://github.com/advisories/GHSA-xmvg-335g-x44q
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-reports-scheduler` — affected >=0 <2.14.0.0

## Details
### Summary

An issue in the OpenSearch reporting plugin allows unintended access to private tenant resources like notebooks. The system did not properly check if the user was the resource author when accessing resources in a private tenant, leading to potential data being revealed.

### Impact

The lack of proper access control validation for private tenant resources in the OpenSearch observability and reporting plugins can lead to unintended data access. If an authorized user with observability or reporting roles is aware of another user's private tenant resource ID, such as a notebook, they can potentially read, modify, or take ownership of that resource, despite not being the original author, thus impacting the confidentiality and integrity of private tenant resources. The impact is confined to private tenant resources, where authorized users may gain inappropriate visibility into data intended to be private from other users within the same OpenSearch instance, potentially violating the intended separation of access. This issue does not alter the scope of access but highlights a flaw in the existing access control mechanisms.

Impacted versions <= 2.13

### Patches

The patches are included in OpenSearch 2.14

### Workarounds

None

### References

OpenSearch 2.14 is available for download at https://opensearch.org/versions/opensearch-2-14-0.html

The latest version of OpenSearch is available for download at https://opensearch.org/downloads.html

## References
- https://github.com/opensearch-project/reporting/security/advisories/GHSA-xmvg-335g-x44q
- https://nvd.nist.gov/vuln/detail/CVE-2024-39900
- https://github.com/opensearch-project/reporting/commit/2403014c57ee63268e83d919db3334b676a8c992
- https://github.com/opensearch-project/reporting
- https://opensearch.org/versions/opensearch-2-14-0.html
