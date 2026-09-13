# [H] CVE-2023-37013

## Summary
Severity: High
Advisory: CVE-2023-37013
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-22
Source: https://osv.dev/vulnerability/CVE-2023-37013
Type: osv

## Details
Open5GS MME versions <= 2.6.4 contains an assertion that can be remotely triggered via a sufficiently large ASN.1 packet over the S1AP interface. An attacker may repeatedly send such an oversized packet to cause the `ogs_sctp_recvmsg` routine to reach an unexpected network state and crash, leading to denial of service.

## References
- https://cellularsecurity.org/ransacked
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37013.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-37013
