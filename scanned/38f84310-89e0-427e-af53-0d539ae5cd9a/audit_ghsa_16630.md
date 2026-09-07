# [H] nautobot has reflected Cross-site Scripting potential in all object list views

## Summary
Severity: High
Advisory: GHSA-jxgr-gcj5-cqqg
CVE: CVE-2024-32979
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-jxgr-gcj5-cqqg
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=1.5.0 <1.6.20
- PyPI: `nautobot` — affected >=2.0.0 <2.2.3

## Details
### Impact

It was discovered that due to improper handling and escaping of user-provided query parameters, a maliciously crafted Nautobot URL could potentially be used to execute a Reflected Cross-Site Scripting (Reflected XSS) attack against users. All filterable object-list views in Nautobot are vulnerable, including:

- /dcim/location-types/
- /dcim/locations/
- /dcim/racks/
- /dcim/rack-groups/
- /dcim/rack-reservations/
- /dcim/rack-elevations/
- /tenancy/tenants/
- /tenancy/tenant-groups/
- /extras/tags/
- /extras/statuses/
- /extras/roles/
- /extras/dynamic-groups/
- /dcim/devices/
- /dcim/platforms/
- /dcim/virtual-chassis/
- /dcim/device-redundancy-groups/
- /dcim/interface-redundancy-groups/
- /dcim/device-types/
- /dcim/manufacturers/
- /dcim/cables/
- /dcim/console-connections/
- /dcim/power-connections/
- /dcim/interface-connections/
- /dcim/interfaces/
- /dcim/front-ports/
- /dcim/rear-ports/
- /dcim/console-ports/
- /dcim/console-server-ports/
- /dcim/power-ports/
- /dcim/power-outlets/
- /dcim/device-bays/
- /dcim/inventory-items/
- /ipam/ip-addresses/
- /ipam/prefixes
- /ipam/rirs/
- /ipam/namespaces/
- /ipam/vrfs/
- /ipam/route-targets/
- /ipam/vlans/
- /ipam/vlan-groups/
- /ipam/services/
- /virtualization/virtual-machines/
- /virtualization/interfaces/
- /virtualization/clusters/
- /virtualization/cluster-types/
- /virtualization/cluster-groups/
- /circuits/circuits/
- /circuits/circuit-types/
- /circuits/providers/
- /circuits/provider-networks/
- /dcim/power-feeds/
- /dcim/power-panels/
- /extras/secrets/
- /extras/secrets-groups/
- /extras/jobs/
- /extras/jobs/scheduled-jobs/approval-queue/
- /extras/jobs/scheduled-jobs/
- /extras/job-results/
- /extras/job-hooks/
- /extras/job-buttons/
- /extras/object-changes/
- /extras/git-repositories/
- /extras/graphql-queries/
- /extras/relationships/
- /extras/notes/
- /extras/config-contexts/
- /extras/config-context-schemas/
- /extras/export-templates/
- /extras/external-integrations/
- /extras/webhooks/
- /extras/computed-fields/
- /extras/custom-fields/
- /extras/custom-links/

as well as any similar object-list views provided by any Nautobot App.

### Patches

Fixed in Nautobot 1.6.20 and 2.2.3.

### Workarounds

No workaround has been identified

### References

- #5646 
- #5647

**Credit to [Michael Panorios](mailto:michael.panorios@pwc.com) for reporting this issue.**

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-jxgr-gcj5-cqqg
- https://nvd.nist.gov/vuln/detail/CVE-2024-32979
- https://github.com/nautobot/nautobot/pull/5646
- https://github.com/nautobot/nautobot/pull/5647
- https://github.com/nautobot/nautobot/commit/2ea5797ea43646d5d8b29433e4c707b5a9758146
- https://github.com/nautobot/nautobot/commit/42440ebd9b381534ad89d62420ebea00d703d64e
- https://github.com/nautobot/nautobot
- https://github.com/nautobot/nautobot/releases/tag/v1.6.20
- https://github.com/nautobot/nautobot/releases/tag/v2.2.3
