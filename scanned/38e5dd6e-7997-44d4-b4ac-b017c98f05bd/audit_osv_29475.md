# [H] CVE-2024-42650

## Summary
Severity: High
Advisory: CVE-2024-42650
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2024-42650
Type: osv

## Details
NanoMQ 0.17.5 was discovered to contain a segmentation fault via the component /nanomq/pub_handler.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted PUBLISH message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42650.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42650
- https://github.com/emqx/nanomq/issues/1168
- https://github.com/nanomq/nanomq/pull/1170
- https://github.com/nanomq/nanomq
