# [H] Resource exhaustion in quiche HTTP/3 and QPACK layers

## Summary
Severity: High
Advisory: CVE-2026-12523
Aliases: GHSA-4fgf-9xrr-88gf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-12523
Type: osv

## Details
Summary



Cloudflare quiche's HTTP/3 layer was discovered to be vulnerable to resource exhaustion (i.e., memory) by means of specially crafted HTTP/3 frames.




Impact



HTTP/3 defines multiple frame types to support HTTP message exchanges and connection management. Each frame has a length and a payload whose length depends on the frame type. quiche was found to be vulnerable when parsing some frame types to pre-allocating memory based on the declared length. An attacker would not need to send the number of declared bytes to trigger this issue.



In addition, quiche was found to not apply QPACK decompression limits correctly. This could allow an attacker to send specially crafted HEADERS frames that would cause more memory commitment than otherwise advertised by MAX_FIELD_SECTION_SIZE (configured by set_max_field_section_size()).






Mitigation:

  *  

Users are requested to upgrade to quiche 0.29.3 which is the earliest version containing the fix for this issue.









Credits: Disclosed responsibly by Sébastien Féry

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12523.json
- https://github.com/cloudflare/quiche/security/advisories/GHSA-4fgf-9xrr-88gf
- https://nvd.nist.gov/vuln/detail/CVE-2026-12523
