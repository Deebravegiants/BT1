# [C] Mass Assignment Vulnerability in mintplex-labs/anything-llm

## Summary
Severity: Critical
Advisory: CVE-2024-0404
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-0404
Type: osv

## Details
A mass assignment vulnerability exists in the `/api/invite/:code` endpoint of the mintplex-labs/anything-llm repository, allowing unauthorized creation of high-privileged accounts. By intercepting and modifying the HTTP request during the account creation process via an invitation link, an attacker can add a `role` property with `admin` value, thereby gaining administrative access. This issue arises due to the lack of property allowlisting and blocklisting, enabling the attacker to exploit the system and perform actions as an administrator.

## References
- https://huntr.com/bounties/b4355bae-766a-4bb0-942b-607bc491b23d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0404.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0404
- https://github.com/mintplex-labs/anything-llm/commit/8cd3a92c660b202655d99bee90b2864694c99946
