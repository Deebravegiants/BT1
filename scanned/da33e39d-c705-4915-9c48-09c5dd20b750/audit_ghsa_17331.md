# [M] snail-job is vulnerable to Code Injection through QLExpressEngine.doEval function

## Summary
Severity: Medium
Advisory: GHSA-3f8c-8h8v-p54h
CVE: CVE-2025-14674
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-14
Source: https://github.com/advisories/GHSA-3f8c-8h8v-p54h
Type: github-advisory

## Affected
- Maven: `com.aizuda:snail-job` — affected >=0 <1.7.0-beta1

## Details
A vulnerability was found in aizuda snail-job up to 1.6.0. Affected by this vulnerability is the function QLExpressEngine.doEval of the file snail-job-common/snail-job-common-core/src/main/java/com/aizuda/snailjob/common/core/expression/strategy/QLExpressEngine.java. The manipulation results in injection. The attack can be launched remotely. Upgrading to version 1.7.0-beta1 addresses this issue. The patch is identified as 978f316c38b3d68bb74d2489b5e5f721f6675e86. The affected component should be upgraded.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-14674
- https://gitee.com/aizuda/snail-job/commit/978f316c38b3d68bb74d2489b5e5f721f6675e86
- https://gitee.com/aizuda/snail-job/issues/ICNUG0
- https://gitee.com/aizuda/snail-job/issues/ICNUG0#note_44321424_link
- https://gitee.com/aizuda/snail-job/releases/tag/vsj1.7.0-beta1
- https://github.com/aizuda/snail-job
- https://vuldb.com/?ctiid.336403
- https://vuldb.com/?id.336403
