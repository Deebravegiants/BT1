# [H] Apache CloudStack: RCE and SSRF in direct download, metalink and NFS templates

## Summary
Severity: High
Advisory: CVE-2026-50112
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-50112
Type: osv

## Details
SSRF via Metalink Mirror URL Resolution:

An authenticated tenant can register a template pointing to an attacker-controlled metalink file containing internal targets. The Secondary Storage VM will retrieve the data and persist it as a template file, which can later be downloaded through normal APIs.

RCE on KVM hypervisor via NFS, Metalink files with/without Direct Downloads:

An authenticated CloudStack tenant holding the default User role can execute arbitrary shell commands as root on the KVM hypervisor host that runs other tenants' VMs. This is cross-tenant root on the underlying compute, reachable via the public CloudStack API.


When a User registers a VM template with directDownload=true and a URL pointing to a .metalink file, the management server fetches the metalink XML and dispatches download to the KVM agent. Inner URLs inside the metalink XML are never re-validated against the scheme allowlist.


These issues affect Apache CloudStack: from 4.14.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.

Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50112.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-50112
