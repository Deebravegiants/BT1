# [H] Excessive permissions for ckan user

## Summary
Severity: High
Advisory: CVE-2023-32696
Aliases: GHSA-c74x-xfvr-x5wg
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-32696
Type: osv

## Details
CKAN is an open-source data management system for powering data hubs and data portals. Prior to versions 2.9.9 and 2.10.1, the `ckan` user (equivalent to www-data) owned code and configuration files in the docker container and the `ckan` user had the permissions to use sudo. These issues allowed for code execution or privilege escalation if an arbitrary file write bug was available. Versions 2.9.9, 2.9.9-dev, 2.10.1, and 2.10.1-dev contain a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32696.json
- https://github.com/ckan/ckan-docker-base/security/advisories/GHSA-c74x-xfvr-x5wg
- https://nvd.nist.gov/vuln/detail/CVE-2023-32696
- https://github.com/ckan/ckan-docker-base/commit/5483c46ce9b518a4e1b626ef7032cce2c1d75c7d
