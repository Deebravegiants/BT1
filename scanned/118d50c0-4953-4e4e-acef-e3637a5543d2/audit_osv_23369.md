# [M] KBase Metrics methods_upload_user_stats.py upload_user_data sql injection

## Summary
Severity: Medium
Advisory: CVE-2022-4860
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-12-30
Source: https://osv.dev/vulnerability/CVE-2022-4860
Type: osv

## Details
A vulnerability was found in KBase Metrics. It has been classified as critical. This affects the function upload_user_data of the file source/daily_cron_jobs/methods_upload_user_stats.py. The manipulation leads to sql injection. The patch is named 959dfb6b05991e30b0fa972a1ecdcaae8e1dae6d. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-217059.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4860.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4860
- https://vuldb.com/?id.217059
- https://github.com/kbase/metrics/pull/77
- https://vuldb.com/?ctiid.217059
- https://github.com/kbase/metrics/commit/959dfb6b05991e30b0fa972a1ecdcaae8e1dae6d
