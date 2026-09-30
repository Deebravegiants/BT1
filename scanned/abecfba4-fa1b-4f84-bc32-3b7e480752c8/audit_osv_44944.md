# [M] MISP Event Template Instantiation Bypasses Sharing Group and Tagging Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-88915
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88915
Type: osv

## Details
Affected versions of MISP do not consistently enforce the acting user's authorization when instantiating event templates.


For templates using distribution = 4, the template can specify a sharing_group_id. The instantiation path passed that value into event creation without verifying that the user instantiating the template was actually permitted to use the selected sharing group. The commit notes that Event::_add() only performed its own sharing-group authorization in another code path, leaving template instantiation able to write the identifier directly.


The same instantiation path also attached template-specified tags without checking the user's normal tagging permissions. In addition, it hardcoded local => 0, meaning tags marked local_only could be attached globally and consequently propagate through synchronization or export, contrary to their intended restriction.


The fix adds explicit SharingGroup::canUse() authorization for the acting user, applies the same tag-modification checks used by normal event tagging, and ensures local_only tags are attached locally.

Version affected: ≤2.5.45

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88915.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-88915
- https://github.com/MISP/MISP/commit/3aa3a9a97
- https://github.com/MISP/MISP
