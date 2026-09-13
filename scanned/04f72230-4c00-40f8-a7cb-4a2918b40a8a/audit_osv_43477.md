# [M] Linuxfabrik Monitoring Plugins: Arbitrary root file disclosure via unconfined --filename in logfile plugin (sudoers LPE)

## Summary
Severity: Medium
Advisory: CVE-2026-73973
Aliases: GHSA-f54c-p5vg-mr5c
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-73973
Type: osv

## Details
Linuxfabrik Monitoring Plugins provides monitoring plugins for Icinga, Nagios, and related systems. Prior to version 7.0.0, check-plugins/logfile/logfile accepted a free-form --filename path and opened it as root when invoked through the shipped nagios or icinga sudoers allowlist, without confining the resolved path to /var/log. An attacker who controls the monitoring account can select a root-readable file such as /etc/shadow and use --warning-regex . while leaving SUPPRESS_OUTPUT false, causing each nonempty line to be collected in warn_matches and returned through lib.base.oao(). The vulnerable flow passes the expanded scan_path directly to open(), and neither real-path containment nor an allowlist protects the sink. The same fix also confines mysql-logfile and openvpn-client-list paths, allows only documented log roots, and resolves symlinks and parent-directory traversal before checking containment. This issue is fixed in version 7.0.0.

## References
- https://github.com/Linuxfabrik/monitoring-plugins/blob/ae486fc629e1ca9373e1b6dd5e395603ee453bbc/CHANGELOG.md#v700---2026-08-14
- https://github.com/Linuxfabrik/monitoring-plugins/releases/tag/v7.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73973.json
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-f54c-p5vg-mr5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-73973
- https://github.com/Linuxfabrik/monitoring-plugins/commit/a0ca1268d84e0caf10442b9c7477d699b52d1c92
