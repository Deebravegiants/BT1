# [H] fs/ntfs3: validate lcns_follow in log_replay conversion

## Summary
Severity: High
Advisory: CVE-2026-64533
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64533
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: validate lcns_follow in log_replay conversion

log_replay() converts DIR_PAGE_ENTRY_32 records into DIR_PAGE_ENTRY
records when replaying version 0 restart tables.

During this conversion, the memmove() length is derived directly from
the on-disk lcns_follow field:

	memmove(&dp->vcn, &dp0->vcn_low,
		2 * sizeof(u64) +
				le32_to_cpu(dp->lcns_follow) * sizeof(u64));

check_rstbl() validates restart table structure, but does not constrain
per-entry lcns_follow values relative to the entry size. A malformed
filesystem image can provide an oversized lcns_follow value, causing
the conversion memmove() to access memory beyond the bounds of the
allocated restart table buffer.

The same field is later used to bound iteration over page_lcns[],
so validating lcns_follow during conversion also prevents downstream
out-of-bounds access from the same malformed metadata.

Compute the maximum valid lcns_follow from the already-validated
restart table entry size and reject entries that exceed this bound.
Reuse the existing t16/t32 scratch variables already declared in
log_replay() to avoid introducing new declarations.

[almaz.alexandrovich@paragon-software.com: fixed the conflicts]

## References
- https://git.kernel.org/stable/c/159f694d682e4215b3822ae31ed3a4631628fe55
- https://git.kernel.org/stable/c/32b9f8733feb241627fa5f564b1a99b5cae974c5
- https://git.kernel.org/stable/c/57c071e2c4f30b9c6f5aacb6679aab1269fbae99
- https://git.kernel.org/stable/c/6a4c53a2e26a865565bd6a460961e8d6fcb32329
- https://git.kernel.org/stable/c/7adb38279812c9c06b0e3fa7382f4d7887f3fa2d
- https://git.kernel.org/stable/c/ca343a99806b4fc8e27c48f08be3445c5fcd1445
- https://git.kernel.org/stable/c/ddfc8683e1a627dbf1b83bacf8961443dd654258
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64533
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
