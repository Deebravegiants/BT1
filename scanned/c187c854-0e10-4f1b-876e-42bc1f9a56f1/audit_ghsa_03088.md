# [H] Local Privilege Escalation in cloudflared

## Summary
Severity: High
Advisory: GHSA-hgwp-4vp4-qmm2
CVE: CVE-2020-24356
CWE: CWE-427
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-hgwp-4vp4-qmm2
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cloudflared` — affected >=0 <0.0.0-20200820025921-9323844ea773

## Details
In `cloudflared` versions < 2020.8.1 (corresponding to 0.0.0-20200820025921-9323844ea773 on pkg.go.dev) on Windows, if an administrator has started `cloudflared` and set it to read configuration files from a certain directory, an unprivileged user can exploit a misconfiguration in order to escalate privileges and execute system-level commands. The misconfiguration was due to the way that `cloudflared` reads its configuration file. One of the locations that `cloudflared` reads from (C:\etc\) is not a secure by default directory due to the fact that Windows does not enforce access controls on this directory without further controls applied. A malformed config.yaml file can be written by any user. Upon reading this config, `cloudflared` would output an error message to a log file defined in the malformed config. The user-controlled log file location could be set to a specific location that Windows will execute when any user logs in.

## References
- https://github.com/cloudflare/cloudflared/security/advisories/GHSA-hgwp-4vp4-qmm2
- https://nvd.nist.gov/vuln/detail/CVE-2020-24356
- https://github.com/cloudflare/cloudflared/commit/9323844ea773b1444460fa09295ab8c01a88d97e
- https://github.com/cloudflare/cloudflared
