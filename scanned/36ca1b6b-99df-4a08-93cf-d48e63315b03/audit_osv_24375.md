# [M] CVE-2023-1095

## Summary
Severity: Medium
Advisory: CVE-2023-1095
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-1095
Type: osv

## Details
In nf_tables_updtable, if nf_tables_table_enable returns an error, nft_trans_destroy is called to free the transaction object. nft_trans_destroy() calls list_del(), but the transaction was never placed on a list -- the list head is all zeroes, this results in a NULL pointer dereference.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1095.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-1095
- https://bugzilla.redhat.com/show_bug.cgi?id=2173973
- https://github.com/torvalds/linux/commit/580077855a40741cf511766129702d97ff02f4d9
