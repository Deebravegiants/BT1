# [H] Exponential catastrophic backtracking (ReDoS) in marked

## Summary
Severity: High
Advisory: CVE-2022-21681
Aliases: GHSA-5v2h-r2cx-5xgj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2022-21681
Type: osv

## Details
Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21681.json
- https://github.com/markedjs/marked/security/advisories/GHSA-5v2h-r2cx-5xgj
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AIXDMC3CSHYW3YWVSQOXAWLUYQHAO5UX/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21681
- https://github.com/markedjs/marked/commit/8f806573a3f6c6b7a39b8cdb66ab5ebb8d55a5f5
