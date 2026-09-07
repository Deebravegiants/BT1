# [H] XSS potential in rendered Markdown fields (comments, description, notes, etc.)

## Summary
Severity: High
Advisory: GHSA-v4xv-795h-rv4h
CVE: CVE-2024-23345
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2024-01-23
Source: https://github.com/advisories/GHSA-v4xv-795h-rv4h
Type: github-advisory

## Affected
- PyPI: `nautobot` — affected >=2.0.0 <2.1.2
- PyPI: `nautobot` — affected >=0 <1.6.10

## Details
### Impact

All users of Nautobot versions earlier than 1.6.10 or 2.1.2 are potentially impacted.

Due to inadequate input sanitization, any user-editable fields that support Markdown rendering, including:

- `Circuit.comments`
- `Cluster.comments`
- `CustomField.description`
- `Device.comments`
- `DeviceRedundancyGroup.comments`
- `DeviceType.comments`
- `Job.description`
- `JobLogEntry.message`
- `Location.comments`
- `Note.note`
- `PowerFeed.comments`
- `Provider.noc_contact`
- `Provider.admin_contact`
- `Provider.comments`
- `ProviderNetwork.comments`
- `Rack.comments`
- `Tenant.comments`
- `VirtualMachine.comments`
- Contents of any custom fields of type `markdown`
- Job class `description` attributes
- The `SUPPORT_MESSAGE` system configuration setting

are potentially susceptible to cross-site scripting (XSS) attacks via maliciously crafted data.

### Patches

Fixed in Nautobot versions 1.6.10 and 2.1.2.

### References

https://github.com/nautobot/nautobot/pull/5133
https://github.com/nautobot/nautobot/pull/5134

## References
- https://github.com/nautobot/nautobot/security/advisories/GHSA-v4xv-795h-rv4h
- https://nvd.nist.gov/vuln/detail/CVE-2024-23345
- https://github.com/nautobot/nautobot/pull/5133
- https://github.com/nautobot/nautobot/pull/5134
- https://github.com/nautobot/nautobot/commit/17effcbe84a72150c82b138565c311bbee357e80
- https://github.com/nautobot/nautobot/commit/64312a4297b5ca49b6cdedf477e41e8e4fd61cce
- https://github.com/nautobot/nautobot
- https://github.com/pypa/advisory-database/tree/main/vulns/nautobot/PYSEC-2024-16.yaml
