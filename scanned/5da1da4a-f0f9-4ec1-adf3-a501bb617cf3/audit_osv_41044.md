# [H] PJSIP: SDP parser out-of-bounds write in remote payload-type map maintenance

## Summary
Severity: High
Advisory: CVE-2026-57159
Aliases: GHSA-rfwg-w9gq-9mw2
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-57159
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to commit 673b978, a remote out-of-bounds read and write can occur in the SDP negotiator when the remote payload-type map maintenance feature is enabled. assign_pt_and_update_map() in pjmedia/src/pjmedia/sdp_neg.c uses payload-type numbers taken from a remote SDP offer or answer to index fixed-size internal tables without sufficient bounds validation, so a crafted remote SDP can cause memory access outside those tables. The practical impact is memory corruption and denial of service; code execution is not demonstrated. This path is only reached when PJMEDIA_SDP_NEG_MAINTAIN_REMOTE_PT_MAP is enabled. The default is disabled, so default builds are not affected; the feature is an interoperability option that integrating products may enable. This issue has been patched via commit 673b978.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57159.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-rfwg-w9gq-9mw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-57159
- https://github.com/pjsip/pjproject/commit/673b978aab1fe3ab874247be32c871acc880cbeb
