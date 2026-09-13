# [H] CVE-2019-3786

## Summary
Severity: High
Advisory: CVE-2019-3786
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2019-04-24
Source: https://osv.dev/vulnerability/CVE-2019-3786
Type: osv

## Details
Cloud Foundry BOSH Backup and Restore CLI, all versions prior to 1.5.0, does not check the authenticity of backup scripts in BOSH. A remote authenticated malicious user can modify the metadata file of a Bosh Backup and Restore job to request extra backup files from different jobs upon restore. The exploited hooks in this metadata script were only maintained in the cfcr-etcd-release, so clusters deployed with the BBR job for etcd in this release are vulnerable.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3786
