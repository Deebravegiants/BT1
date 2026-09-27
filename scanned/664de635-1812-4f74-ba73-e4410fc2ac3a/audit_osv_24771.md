# [C] CVE-2023-26463

## Summary
Severity: Critical
Advisory: CVE-2023-26463
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-14
Source: https://osv.dev/vulnerability/CVE-2023-26463
Type: osv

## Details
strongSwan 5.9.8 and 5.9.9 potentially allows remote code execution because it uses a variable named "public" for two different purposes within the same function. There is initially incorrect access control, later followed by an expired pointer dereference. One attack vector is sending an untrusted client certificate during EAP-TLS. A server is affected only if it loads plugins that implement TLS-based EAP methods (EAP-TLS, EAP-TTLS, EAP-PEAP, or EAP-TNC). This is fixed in 5.9.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26463.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26463
- https://security.netapp.com/advisory/ntap-20230517-0010/
- https://github.com/strongswan/strongswan/releases
- https://www.strongswan.org/blog/2023/03/02/strongswan-vulnerability-%28cve-2023-26463%29.html
