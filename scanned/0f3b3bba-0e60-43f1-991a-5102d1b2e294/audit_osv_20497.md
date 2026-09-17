# [M] CVE-2021-3429

## Summary
Severity: Medium
Advisory: CVE-2021-3429
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2021-3429
Type: osv

## Details
When instructing cloud-init to set a random password for a new user account, versions before 21.2 would write that password to the world-readable log file /var/log/cloud-init-output.log. This could allow a local user to log in as another user.

## References
- https://github.com/canonical/cloud-init/commit/b794d426b9ab43ea9d6371477466070d86e10668
