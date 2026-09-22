# [C] Wazuh cluster worker file sync allows arbitrary file write under /var/ossec (incomplete fix for CVE-2026-30893)

## Summary
Severity: Critical
Advisory: CVE-2026-61800
Aliases: GHSA-3jff-488g-335f
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-61800
Type: osv

## Details
Wazuh is an open-source security platform providing unified XDR and SIEM protection for endpoints and cloud workloads. In versions 4.4.0 through 4.14.6, a party holding the cluster key can write, overwrite, or delete arbitrary files under /var/ossec on worker nodes, leading to remote code execution as root. During cluster file synchronization, the non-merged branch of update_master_files_in_worker() moves each staged file to a destination derived only from safe_join(), which confines the path to /var/ossec but never verifies that the file lands in the directory declared by its cluster_item_key. Because the destination check present on the primary node and on the worker's merged branch was not applied, a peer can place files at attacker-chosen locations under /var/ossec, including paths that are executed as root, and the delete branch has the same gap. This is an incomplete fix for CVE-2026-30893, which addressed traversal outside /var/ossec but left this path able to redirect files anywhere within it. This issue is fixed in version 4.14.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61800.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-3jff-488g-335f
- https://nvd.nist.gov/vuln/detail/CVE-2026-61800
- https://github.com/wazuh/wazuh/commit/f7f7c4d2d9e683c5d42e997fe7028a3fb2578853
