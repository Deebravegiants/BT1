# [M] CVE-2022-47933

## Summary
Severity: Medium
Advisory: CVE-2022-47933
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-24
Source: https://osv.dev/vulnerability/CVE-2022-47933
Type: osv

## Details
Brave Browser before 1.42.51 allowed a remote attacker to cause a denial of service via a crafted HTML file that references the IPFS scheme. This vulnerability is caused by an uncaught exception in the function ipfs::OnBeforeURLRequest_IPFSRedirectWork() in ipfs_redirect_network_delegate_helper.cc.

## References
- https://hackerone.com/reports/1610343
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/47xxx/CVE-2022-47933.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-47933
- https://github.com/brave/brave-browser/issues/23646
- https://github.com/brave/brave-browser/issues/24378
- https://github.com/brave/brave-core/commit/7ef8cb2f232abdf59ec9c3c99a086a14b972bc56
- https://github.com/brave/brave-core/pull/13989
