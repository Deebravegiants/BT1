# [C] CVE-2026-57898

## Summary
Severity: Critical
Advisory: CVE-2026-57898
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-57898
Type: osv

## Details
In Eclipse BaSyx Java Server SDK versions 2.0.0-milestone-05 to 2.0.0-milestone-12, deployments using the MongoDB backend are vulnerable to an unauthenticated arbitrary file write through the AAS thumbnail API.




The AAS thumbnail upload path accepted a client-controlled fileName request parameter and passed it through repository file handling as both a repository key and, during thumbnail retrieval, a local filesystem path. With the MongoDB file repository, the supplied filename was treated as an opaque GridFS key and was not normalized or restricted as a filesystem path. A remote attacker could upload thumbnail content using an absolute or traversal-style filename, then trigger thumbnail retrieval so that the uploaded bytes were written to the attacker-chosen path on the server filesystem.




This could allow writing files anywhere the Java process has permission to write and may lead to remote code execution. The default InMemory backend is not affected by this specific path because it normalizes and restricts file paths to its temporary directory.




The issue is fixed in Eclipse BaSyx Java Server SDK 2.0.0-milestone-13.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/159
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57898.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57898
- https://github.com/eclipse-basyx/basyx-java-server-sdk
