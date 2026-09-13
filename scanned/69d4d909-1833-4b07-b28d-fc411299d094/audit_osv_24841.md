# [C] CVE-2023-27573

## Summary
Severity: Critical
Advisory: CVE-2023-27573
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2023-27573
Type: osv

## Details
netbox-docker before 2.5.0 has a superuser account with default credentials (admin password for the admin account, and 0123456789abcdef0123456789abcdef01234567 value for SUPERUSER_API_TOKEN). In practice on the public Internet, almost all users changed the password but only about 90% changed the token. Having a default token value was intentional and was valuable for the main intended use case of the netbox-docker product (isolated development networks). Some users engaged in an effort to repurpose netbox-docker for production. The documentation for this effort stated that the defaults must not be used. However, installation did not ensure non-default values. The Supplier was aware of the CVE ID assignment and did not object to the assignment.

## References
- https://github.com/netbox-community/netbox-docker/releases/tag/2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27573.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27573
- https://github.com/netbox-community/netbox-docker/issues/953
- https://github.com/netbox-community/netbox-docker/pull/959
