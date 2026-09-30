# [M] Limited Authentication Bypass for Media Files

## Summary
Severity: Medium
Advisory: GHSA-qm6v-cg9v-53j3
CVE: CVE-2022-29237
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-qm6v-cg9v-53j3
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-ingest-service-impl` — affected >=0 <10.14
- Maven: `org.opencastproject:opencast-ingest-service-impl` — affected >=11.0 <11.7

## Details
Prior to Opencast 10.14 and 11.7, users could pass along URLs for files belonging to organizations other than the user's own, which Opencast would then import into the current organization, bypassing organizational barriers.

### Impact

The vulnerability allows attackers to bypass organizational barriers. Attackers must have full access to Opencast's ingest REST interface, and also know internal links to resources in another organization of the same Opencast cluster.

If you do not run a multi-tenant cluster, you are not affected by this issue.

### Patches

This issue is fixed in Opencast 10.14 and 11.7.

### References

- [Patch fixing the issue](https://github.com/opencast/opencast/commit/8d5ec1614eed109b812bc27b0c6d3214e456d4e7)

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
* Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-qm6v-cg9v-53j3
- https://nvd.nist.gov/vuln/detail/CVE-2022-29237
- https://github.com/opencast/opencast/commit/8d5ec1614eed109b812bc27b0c6d3214e456d4e7
- https://github.com/opencast/opencast
