# [M] CVE-2019-12215

## Summary
Severity: Medium
Advisory: CVE-2019-12215
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12215
Type: osv

## Details
A full path disclosure vulnerability was discovered in Matomo v3.9.1 where a user can trigger a particular error to discover the full path of Matomo on the disk, because lastError.file is used in plugins/CorePluginsAdmin/templates/safemode.twig. NOTE: the vendor disputes the significance of this issue, stating "avoid reporting path disclosures, as we don't consider them as security vulnerabilities.

## References
- https://github.com/matomo-org/matomo/issues/14464
