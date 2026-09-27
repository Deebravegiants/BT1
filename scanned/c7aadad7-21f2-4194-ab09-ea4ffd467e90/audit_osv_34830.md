# [H] CVE-2025-65559

## Summary
Severity: High
Advisory: CVE-2025-65559
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-65559
Type: osv

## Details
An issue was discovered in Open5GS 2.7.5-49-g465e90f, when processing a PFCP Session Establishment Request (type=50), the UPF crashes with a reachable assertion in `lib/pfcp/context.c` (`ogs_pfcp_object_teid_hash_set`) if the CreatePDR?PDI?F-TEID has CH=1 and the F-TEID address-family flag(s) (IPv4/IPv6) do not match the GTP-U resource family configured for the selected DNN (Network Instance), resulting in a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65559.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65559
- https://github.com/open5gs/open5gs/issues/4135
