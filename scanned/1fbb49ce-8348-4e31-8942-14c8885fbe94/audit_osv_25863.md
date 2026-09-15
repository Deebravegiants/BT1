# [M] FOG path traversal via unauthenticated endpoint

## Summary
Severity: Medium
Advisory: CVE-2023-46237
Aliases: GHSA-ffp9-rhfm-98c2
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-46237
Type: osv

## Details
FOG is a free open-source cloning/imaging/rescue suite/inventory management system. Prior to version 1.5.10, an endpoint intended to offer limited enumeration abilities to authenticated users was accessible to unauthenticated users. This enabled unauthenticated users to discover files and their respective paths that were visible to the Apache user group. Version 1.5.10 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46237.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-ffp9-rhfm-98c2
- https://nvd.nist.gov/vuln/detail/CVE-2023-46237
- https://github.com/FOGProject/fogproject/commit/68d73740d7d40aee77cfda3fb8199d58bf04f48b
