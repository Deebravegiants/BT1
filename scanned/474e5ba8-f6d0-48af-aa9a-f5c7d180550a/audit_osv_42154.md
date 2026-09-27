# [C] Apache Fory, Apache Fory: Out-of-Bounds Read via sun.misc.Unsafe in zero-copy java deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-64609
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-64609
Type: osv

## Details
Out-of-bounds read via sun.misc.Unsafe in Apache Fory. When out-of-band zero-copy deserialization is used, readAlignedVarUint() can read beyond the bounds of the underlying buffer. Out-of-band zero-copy deserialization is an opt-in feature; applications that do not use it are not affected.

This issue affects Apache Fory (formerly Apache Fury): from 0.5.0 before 1.4.0. Versions before 0.11.0 were published under the Maven coordinates org.apache.fury:fury-core.

Users are recommended to upgrade to version 1.4.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/21/6
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64609.json
- https://lists.apache.org/thread/rdv22ks3b0cxh0r52w3ghxgkxqso3f1b
- https://nvd.nist.gov/vuln/detail/CVE-2026-64609
