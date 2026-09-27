# [C] Iris Allows Arbitrary File Deletion via Mass Assignment in Datastore File Management

## Summary
Severity: Critical
Advisory: CVE-2026-22783
Aliases: GHSA-qhqj-8qw6-wp8v
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22783
Type: osv

## Details
Iris is a web collaborative platform that helps incident responders share technical details during investigations. Prior to 2.4.24, the DFIR-IRIS datastore file management system has a vulnerability where mass assignment of the file_local_name field combined with path trust in the delete operation enables authenticated users to delete arbitrary filesystem paths. The vulnerability manifests through a three-step attack chain: authenticated users upload a file to the datastore, update the file's file_local_name field to point to an arbitrary filesystem path through mass assignment, then trigger the delete operation which removes the target file without path validation. This vulnerability is fixed in 2.4.24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22783.json
- https://github.com/dfir-iris/iris-web/security/advisories/GHSA-qhqj-8qw6-wp8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-22783
- https://github.com/dfir-iris/iris-web/commit/57c1b80494bac187893aebc6d9df1ce6e56485b7
