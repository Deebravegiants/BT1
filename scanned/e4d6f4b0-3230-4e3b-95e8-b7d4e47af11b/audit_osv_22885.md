# [H] A Remote Code Injection vulnerability exists in CERT software prior to version 1.50.5

## Summary
Severity: High
Advisory: CVE-2022-40238
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-40238
Type: osv

## Details
A Remote Code Injection vulnerability exists in CERT software prior to version 1.50.5. An authenticated attacker can inject arbitrary pickle object as part of a user's profile. This can lead to code execution on the server when the user's profile is accessed.

## References
- https://github.com/CERTCC/VINCE/issues?q=label%3Asecurity
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40238.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40238
