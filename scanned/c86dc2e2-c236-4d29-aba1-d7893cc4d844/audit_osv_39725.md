# [H] Windmill < 1.703.2 Incorrect Default Permissions in nsjail Configuration

## Summary
Severity: High
Advisory: CVE-2026-47107
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-47107
Type: osv

## Details
Windmill prior to 1.703.2 contains an incorrect default permissions vulnerability in nsjail sandbox configuration files where /etc is bind-mounted without read-write restrictions, allowing authenticated users to write arbitrary entries to /etc/hosts, /etc/resolv.conf, and /etc/ssl/certs/ca-certificates.crt from within script execution sandboxes. Attackers can exploit persistent poisoned entries across all subsequent script executions on the same worker pod to redirect hostnames, intercept DNS queries, perform transparent HTTPS man-in-the-middle attacks, and intercept WM_TOKEN JWTs to gain workspace-admin access to other users' workspaces.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47107.json
- https://github.com/windmill-labs/windmill/releases/tag/v1.703.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-47107
- https://www.vulncheck.com/advisories/windmill-incorrect-default-permissions-in-nsjail-configuration
- https://github.com/windmill-labs/windmill/pull/9194
- https://github.com/windmill-labs/windmill/commit/f8467f38c8a053117ce62f96684cfb15ef792f08
- https://github.com/windmill-labs/windmill
