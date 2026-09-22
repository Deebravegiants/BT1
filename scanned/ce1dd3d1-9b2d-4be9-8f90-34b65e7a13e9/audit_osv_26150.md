# [H] CVE-2023-51939

## Summary
Severity: High
Advisory: CVE-2023-51939
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-01
Source: https://osv.dev/vulnerability/CVE-2023-51939
Type: osv

## Details
An issue in the cp_bbs_sig function in relic/src/cp/relic_cp_bbs.c of Relic relic-toolkit 0.6.0 allows a remote attacker to obtain sensitive information and escalate privileges via the cp_bbs_sig function.

## References
- https://gist.github.com/liang-junkai/1b59487c0f7002fa5da98035b53e409f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51939.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51939
- https://github.com/relic-toolkit/relic/issues/284
- https://github.com/liang-junkai/Relic-bbs-fault-injection
