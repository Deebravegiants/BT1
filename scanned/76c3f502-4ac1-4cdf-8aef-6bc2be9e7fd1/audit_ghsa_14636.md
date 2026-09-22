# [H] Gogs allows argument Injection when tagging new releases

## Summary
Severity: High
Advisory: GHSA-m27m-h5gj-wwmg
CVE: CVE-2024-39933
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AC:L/AV:N/A:N/C:H/I:N/PR:L/S:C/UI:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-m27m-h5gj-wwmg
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.1

## Details
### Impact

Unprivileged user accounts with at least one SSH key can read arbitrary files on the system. For instance, they could leak the configuration files that could contain database credentials (`[database] *`) and `[security] SECRET_KEY`. Attackers could also exfiltrate TLS certificates, other users' repositories, and the Gogs database when the SQLite driver is enabled.

### Patches

Unintended Git options has been ignored for creating tags (https://github.com/gogs/gogs/pull/7872). Users should upgrade to 0.13.1 or the latest 0.14.0+dev.

### Workarounds

No viable workaround available, please only grant access to trusted users to your Gogs instance on affected versions.

### References

https://www.cve.org/CVERecord?id=CVE-2024-39933

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-m27m-h5gj-wwmg
- https://nvd.nist.gov/vuln/detail/CVE-2024-39933
- https://github.com/gogs/gogs/pull/7872
- https://github.com/gogs/gogs/commit/76831d0d06c44c5cf46dc22b380440b7507c2f07
- https://github.com/gogs/gogs
- https://www.sonarsource.com/blog/securing-developer-tools-unpatched-code-vulnerabilities-in-gogs-1
