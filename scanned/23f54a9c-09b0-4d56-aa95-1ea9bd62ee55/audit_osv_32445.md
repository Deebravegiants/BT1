# [H] kanidm-provision leaks provisioned admin credentials into the system log

## Summary
Severity: High
Advisory: CVE-2025-30205
Aliases: GHSA-57fc-pcqm-53rp
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:N)
Published: 2025-03-24
Source: https://osv.dev/vulnerability/CVE-2025-30205
Type: osv

## Details
kanidim-provision is a helper utility that uses kanidm's API to provision users, groups and oauth2 systems. Prior to version 1.2.0, a faulty function intrumentation in the (optional) kanidm patches provided by kandim-provision will cause the provisioned admin credentials to be leaked to the system log. This only impacts users which both use the provided patches and provision their `admin` or `idm_admin` account credentials this way. No other credentials are affected. Users should recompile kanidm with the newest patchset from tag `v1.2.0` or higher. As a workaround, the user can set the log level `KANIDM_LOG_LEVEL` to any level higher than `info`, for example `warn`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30205.json
- https://github.com/oddlama/kanidm-provision/security/advisories/GHSA-57fc-pcqm-53rp
- https://nvd.nist.gov/vuln/detail/CVE-2025-30205
- https://github.com/oddlama/kanidm-provision/commit/a102b52e4a79be4263068577ba837f16c3e487a2
