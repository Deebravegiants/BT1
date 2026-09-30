# [H] CVE-2025-29646

## Summary
Severity: High
Advisory: CVE-2025-29646
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-29646
Type: osv

## Details
An issue in upf in open5gs 2.7.2 and earlier allows a remote attacker to cause a Denial of Service via a crafted PFCP SessionEstablishmentRequest packet with restoration indication = true and (teid = 0 or teid >= ogs_pfcp_pdr_teid_pool.size).

## References
- https://gist.github.com/scmdcs/581fa485f957239ea5551daa173d0189
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29646.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29646
- https://github.com/open5gs/open5gs/issues/3747
