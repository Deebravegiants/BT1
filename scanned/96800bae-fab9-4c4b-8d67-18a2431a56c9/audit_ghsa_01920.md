# [M] Privilege Escalation in fscrypt

## Summary
Severity: Medium
Advisory: GHSA-qj26-7grj-whg3
CVE: CVE-2018-6558
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-qj26-7grj-whg3
Type: github-advisory

## Affected
- Go: `github.com/google/fscrypt` — affected >=0 <0.2.4

## Details
The pam_fscrypt module in fscrypt before 0.2.4 may incorrectly restore primary and supplementary group IDs to the values associated with the root user, which allows attackers to gain privileges via a successful login through certain applications that use Linux-PAM (aka pam).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6558
- https://github.com/google/fscrypt/issues/77
- https://github.com/google/fscrypt/commit/3022c1603d968c22f147b4a2c49c4637dd1be91b
- https://github.com/google/fscrypt/commit/315f9b042237200174a1fb99427f74027e191d66
- https://github.com/google/fscrypt
- https://launchpad.net/bugs/1787548
- https://pkg.go.dev/vuln/GO-2020-0027
