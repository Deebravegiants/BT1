# [H] CVE-2023-23759

## Summary
Severity: High
Advisory: CVE-2023-23759
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-23759
Type: osv

## Details
There is a vulnerability in the fizz library prior to v2023.01.30.00 where a CHECK failure can be triggered remotely. This behavior requires the client supported cipher advertisement changing between the original ClientHello and the second ClientHello, crashing the process (impact is limited to denial of service).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23759.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23759
- https://www.facebook.com/security/advisories/cve-2023-23759
- https://github.com/facebookincubator/fizz/commit/8d3649841597bedfb6986c30431ebad0eb215265
