# [C] Harbor allows the use of the default password for web UI login

## Summary
Severity: Critical
Advisory: GHSA-hj7x-hmf2-hc2p
CVE: CVE-2026-4404
CWE: CWE-1393, CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-hj7x-hmf2-hc2p
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=0

## Details
Use of hard coded credentials in GoHarbor Harbor version 2.15.0 and below, allows attackers to use the default password and gain access to the web UI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4404
- https://github.com/goharbor/harbor/issues/1937
- https://github.com/goharbor/harbor/pull/22751
- https://github.com/goharbor/harbor
- https://goharbor.io/docs/1.10/install-config/run-installer-script/#:~:text=If%20you%20did%20not%20change%20them%20in%20harbor.yml,%20the%20default%20administrator%20username%20and%20password%20are%20admin%20and%20Harbor12345
- https://www.kb.cert.org/vuls/id/577436
