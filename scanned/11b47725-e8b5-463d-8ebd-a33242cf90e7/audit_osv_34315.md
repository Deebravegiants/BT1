# [M] OpenEBS Local PV RawFile persistent volume data is world readable

## Summary
Severity: Medium
Advisory: CVE-2025-58061
Aliases: GHSA-wh95-vw4r-xwx4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-08-28
Source: https://osv.dev/vulnerability/CVE-2025-58061
Type: osv

## Details
OpenEBS Local PV RawFile allows dynamic deployment of Stateful Persistent Node-Local Volumes & Filesystems for Kubernetes. Prior to version 0.10.0, persistent volume data is world readable and that would allow non-privileged users to access sensitive data such as databases of k8s workload. The rawfile-localpv storage class creates persistent volume data under /var/csi/rawfile/ on Kubernetes hosts by default. However, the directory and data in it are world-readable. It allows non-privileged users to access the whole persistent volume data, and those can include sensitive information such as a whole database if the Kubernetes tenants are running MySQL or PostgreSQL in a container so it could lead to a database breach. This issue has been patched in version 0.10.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58061.json
- https://github.com/openebs/rawfile-localpv/security/advisories/GHSA-wh95-vw4r-xwx4
- https://nvd.nist.gov/vuln/detail/CVE-2025-58061
