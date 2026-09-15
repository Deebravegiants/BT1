# [H] CVE-2023-33659

## Summary
Severity: High
Advisory: CVE-2023-33659
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-06
Source: https://osv.dev/vulnerability/CVE-2023-33659
Type: osv

## Details
A heap buffer overflow vulnerability exists in NanoMQ 0.17.2. The vulnerability can be triggered by calling the function nmq_subinfo_decode() in the file mqtt_parser.c. An attacker could exploit this vulnerability to cause a denial of service attack.

## References
- https://github.com/nanomq/NanoNNG/pull/509/commits/6815c4036a2344865da393803ecdb7af27d8bde1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33659.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33659
- https://github.com/emqx/nanomq/issues/1154
- https://github.com/emqx/nanomq
