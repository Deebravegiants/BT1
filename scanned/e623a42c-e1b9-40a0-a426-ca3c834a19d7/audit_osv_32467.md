# [C] CVE-2025-30472

## Summary
Severity: Critical
Advisory: CVE-2025-30472
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-22
Source: https://osv.dev/vulnerability/CVE-2025-30472
Type: osv

## Details
Corosync through 3.1.9, if encryption is disabled or the attacker knows the encryption key, has a stack-based buffer overflow in orf_token_endian_convert in exec/totemsrp.c via a large UDP packet.

## References
- https://corosync.org
- https://github.com/corosync/corosync/blob/73ba225cc48ebb1903897c792065cb5e876613b0/exec/totemsrp.c#L4677
- https://lists.debian.org/debian-lts-announce/2025/09/msg00023.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30472.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30472
- https://github.com/corosync/corosync/issues/778
