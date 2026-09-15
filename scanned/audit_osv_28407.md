# [H] CVE-2024-32487

## Summary
Severity: High
Advisory: CVE-2024-32487
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-04-13
Source: https://osv.dev/vulnerability/CVE-2024-32487
Type: osv

## Details
less through 653 allows OS command execution via a newline character in the name of a file, because quoting is mishandled in filename.c. Exploitation typically requires use with attacker-controlled file names, such as the files extracted from an untrusted archive. Exploitation also requires the LESSOPEN environment variable, but this is set by default in many common cases.

## References
- https://www.openwall.com/lists/oss-security/2024/04/12/5
- https://www.openwall.com/lists/oss-security/2024/04/13/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32487.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32487
- https://security.netapp.com/advisory/ntap-20240605-0009/
- https://github.com/gwsw/less/commit/007521ac3c95bc76e3d59c6dbfe75d06c8075c33
- http://www.openwall.com/lists/oss-security/2024/04/15/1
- https://lists.debian.org/debian-lts-announce/2024/05/msg00018.html
