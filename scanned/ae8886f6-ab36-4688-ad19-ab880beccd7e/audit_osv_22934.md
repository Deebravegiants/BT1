# [H] CVE-2022-41347

## Summary
Severity: High
Advisory: CVE-2022-41347
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-41347
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 8.8.x and 9.x (e.g., 8.8.15). The Sudo configuration permits the zimbra user to execute the NGINX binary as root with arbitrary parameters. As part of its intended functionality, NGINX can load a user-defined configuration file, which includes plugins in the form of .so files, which also execute as root.

## References
- https://darrenmartyn.ie/2021/10/25/zimbra-nginx-local-root-exploit/
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41347.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41347
- https://github.com/darrenmartyn/zimbra-hinginx
