# [H] BACnet-stack MS/TP reply matcher OOB read

## Summary
Severity: High
Advisory: CVE-2025-66624
Aliases: GHSA-8wgw-5h6x-qgqg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66624
Type: osv

## Details
BACnet Protocol Stack library provides a BACnet application layer, network layer and media access (MAC) layer communications services. Prior to 1.5.0.rc2, The npdu_is_expected_reply function in src/bacnet/npdu.c indexes request_pdu[offset+2/3/5] and reply_pdu[offset+1/2/4] without verifying that those APDU bytes exist. bacnet_npdu_decode() can return offset == 2 for a 2-byte NPDU, so tiny PDUs pass the version check and then get read out of bounds. On ASan/MPU/strict builds this is an immediate crash (DoS). On unprotected builds it is undefined behavior and can mis-route replies; RCE is unlikely because only reads occur, but DoS is reliable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66624.json
- https://github.com/bacnet-stack/bacnet-stack/security/advisories/GHSA-8wgw-5h6x-qgqg
- https://nvd.nist.gov/vuln/detail/CVE-2025-66624
- https://github.com/bacnet-stack/bacnet-stack/commit/9378f7d1e70169ebde4a5090bae7603703eadf48
