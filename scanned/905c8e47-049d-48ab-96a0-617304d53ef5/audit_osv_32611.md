# [M] Harden-Runner Evasion of 'disable-sudo' policy

## Summary
Severity: Medium
Advisory: CVE-2025-32955
Aliases: GHSA-mxr3-8whj-j74r
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-04-21
Source: https://osv.dev/vulnerability/CVE-2025-32955
Type: osv

## Details
Harden-Runner is a CI/CD security agent that works like an EDR for GitHub Actions runners. Versions from 0.12.0 to before 2.12.0 are vulnerable to `disable-sudo` bypass. Harden-Runner includes a policy option `disable-sudo` to prevent the GitHub Actions runner user from using sudo. This is implemented by removing the runner user from the sudoers file. However, this control can be bypassed as the runner user, being part of the docker group, can interact with the Docker daemon to launch privileged containers or access the host filesystem. This allows the attacker to regain root access or restore the sudoers file, effectively bypassing the restriction. This issue has been patched in version 2.12.0.

## References
- https://github.com/step-security/harden-runner/releases/tag/v2.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32955.json
- https://github.com/step-security/harden-runner/security/advisories/GHSA-mxr3-8whj-j74r
- https://nvd.nist.gov/vuln/detail/CVE-2025-32955
- https://github.com/step-security/harden-runner/commit/0634a2670c59f64b4a01f0f96f84700a4088b9f0
