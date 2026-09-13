# [C] Nomad Unauthenticated Client Agent HTTP Request Privilege Escalation

## Summary
Severity: Critical
Advisory: CVE-2023-1782
Aliases: GHSA-f8r8-h93m-mj77, GO-2023-1707
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-1782
Type: osv

## Details
HashiCorp Nomad and Nomad Enterprise versions 1.5.0 up to 1.5.2 allow unauthenticated users to bypass intended ACL authorizations for clusters where mTLS is not enabled. This issue is fixed in version 1.5.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2023-12-nomad-unauthenticated-client-agent-http-request-privilege-escalation/52375
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1782.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1782
- https://github.com/hashicorp/nomad
