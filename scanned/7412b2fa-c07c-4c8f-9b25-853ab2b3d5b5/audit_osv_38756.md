# [C] jadx: RCE Via Groovy Code Injection in Gradle Export

## Summary
Severity: Critical
Advisory: CVE-2026-42049
Aliases: GHSA-w6f5-h4x4-rfpj
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-42049
Type: osv

## Details
jadx is a Dex to Java decompiler. Prior to 1.5.6, jadx inserts the android:versionName value from an AndroidManifest into the generated app/build.gradle Groovy template without proper sanitization when exporting a decompiled APK as an Android Gradle project. A malicious APK can break out of the string context so that opening or building the exported Gradle project executes attacker-controlled Groovy code on the victim machine. This issue is fixed in version 1.5.6.

## References
- https://github.com/skylot/jadx/releases/tag/v1.5.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42049.json
- https://github.com/skylot/jadx/security/advisories/GHSA-w6f5-h4x4-rfpj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42049
- https://github.com/skylot/jadx/commit/5a6e660b4663d998d52c7dc4511299f3368ef611
