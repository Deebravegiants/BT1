# [H] Below has Incorrect Permission Assignment for Critical Resource

## Summary
Severity: High
Advisory: GHSA-9mc5-7qhg-fp3w
CVE: CVE-2025-27591
CWE: CWE-732
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-9mc5-7qhg-fp3w
Type: github-advisory

## Affected
- crates.io: `below` — affected >=0 <0.9.0

## Details
### Impact
A privilege escalation vulnerability existed in the Below service prior to v0.9.0 due to the creation of a world-writable directory at /var/log/below. This could have allowed local unprivileged users to escalate to root privileges through symlink attacks that manipulate files such as /etc/shadow.

### Patches
https://github.com/facebookincubator/below/commit/10e73a21d67baa2cd613ee92ce999cda145e1a83

This is included in version 0.9.0

### Workarounds
Change the permission on `/var/log/below` manually

### References
https://www.facebook.com/security/advisories/cve-2025-27591
https://www.cve.org/CVERecord?id=CVE-2025-27591

## References
- https://github.com/facebookincubator/below/security/advisories/GHSA-9mc5-7qhg-fp3w
- https://nvd.nist.gov/vuln/detail/CVE-2025-27591
- https://github.com/facebookincubator/below/commit/10e73a21d67baa2cd613ee92ce999cda145e1a83
- https://github.com/facebookincubator/below/commit/da9382e6e3e332fd2c3195e22f34977f83f0f1f3
- https://github.com/facebookincubator/below
- https://rustsec.org/advisories/RUSTSEC-2025-0149.html
- https://www.facebook.com/security/advisories/cve-2025-27591
- https://www.openwall.com/lists/oss-security/2025/03/12/1
- http://www.openwall.com/lists/oss-security/2025/03/12/1
