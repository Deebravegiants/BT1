# [M] xrdp: Out-of-bounds read in GCC Conference Create Request CS_SECURITY processing (xrdp_sec_process_mcs_data_CS_SECURITY)

## Summary
Severity: Medium
Advisory: CVE-2026-55639
Aliases: GHSA-6g36-mxcf-r3gc
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-55639
Type: osv

## Details
xrdp is an open source RDP server. Versions 0.10.6 and prior contain a vulnerability concerning the parsing of Client Security Data within the Client MCS Connect Initial PDU with GCC Conference Create Request during the connection sequence. During the initial capability and security negotiation phase, the parser fails to perform sufficient length validation for the incoming data block. A remote, unauthenticated attacker could potentially exploit this flaw by sending a specially crafted RDP packet containing malformed data. Due to missing bounds checks, the xrdp process may read a small number of bytes beyond the declared data block boundary, potentially disclosing process memory contents that could be combined with other vulnerabilities. This issue has been fixed in version 0.10.6.1.

## References
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.10.6.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55639.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-6g36-mxcf-r3gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-55639
