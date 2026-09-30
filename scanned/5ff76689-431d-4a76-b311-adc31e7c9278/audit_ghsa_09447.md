# [M] Nautobot: REST API permits creation of GenericForeignKey references to objects that the user should not be able to reference

## Summary
Severity: Medium
Advisory: GHSA-wpxj-44w3-2j6x
CVE: CVE-2026-44794
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-wpxj-44w3-2j6x
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=3.0.0a2 <3.1.2
- PyPI: `nautobot` — affected >=0 <2.4.33

## Details
### Impact

In the case of inter-object references via `GenericForeignKey` (a pattern allowing an object to reference another object that may belong to one of several different "content types" or database tables), when creating or updating an object containing a `GenericForeignKey`, Nautobot's REST API failed to enforce user "view" permissions when determining whether a given reference to another object would be valid. 

As a concrete example, a user:

- who has permission to create or update `ImageAttachment` records
- but who lacks permission to view (some or all) `Device` records
- _but who knows (via some other mechanism) the UUID of a specific `Device` that they do not otherwise have access to_

could create via the REST API an `ImageAttachment` linked to that specific `Device`.

Other models that use `GenericForeignKey` and may be writable via the REST API, and hence have a similar vulnerability to `ImageAttachment`, may include:

- `ApprovalWorkflow`
- `Cable`
- `ConfigContext`
- `ContactAssociation`
- `DataCompliance`
- `Device`
- `ExportTemplate`
- `GraphQLQuery`
- `Note`
- `ObjectMetadata`
- `RelationshipAssociation`
- `StaticGroupAssociation`
- `VirtualMachine`

Additionally, any Nautobot Apps that provide models with a REST API and use GenericForeignKey may have a similar vulnerability for their models.

### Patches

A general-purpose fix has been implemented in Nautobot 2.4.33 and 3.1.2, which ensures correct application of "view" permissions when creating or modifying object references via `GenericForeignKey` throughout the REST API. Individual models/views/serializers generally will not require any specific code changes to benefit from this fix.

### Workarounds

No known workarounds at this time.

### References

- 2.4.33 (<a href="https://github.com/nautobot/nautobot/commit/9918bdb9bcf1eb42cda72c344f420a64ef7665f1">patch</a>)
- 3.1.2 (<a href="https://github.com/nautobot/nautobot/commit/36cde7148a207234de6212ec074f321dbc9d1b5b">patch</a>)

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-wpxj-44w3-2j6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-44794
- https://github.com/nautobot/nautobot/commit/36cde7148a207234de6212ec074f321dbc9d1b5b
- https://github.com/nautobot/nautobot/commit/9918bdb9bcf1eb42cda72c344f420a64ef7665f1
- https://github.com/nautobot/nautobot
- https://github.com/nautobot/nautobot/releases/tag/v2.4.33
- https://github.com/nautobot/nautobot/releases/tag/v3.1.2
