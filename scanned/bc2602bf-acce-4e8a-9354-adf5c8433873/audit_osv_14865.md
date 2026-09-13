# [H] CVE-2019-12083

## Summary
Severity: High
Advisory: CVE-2019-12083
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-13
Source: https://osv.dev/vulnerability/CVE-2019-12083
Type: osv

## Details
The Rust Programming Language Standard Library 1.34.x before 1.34.2 contains a stabilized method which, if overridden, can violate Rust's safety guarantees and cause memory unsafety. If the `Error::type_id` method is overridden then any type can be safely cast to any other type, causing memory safety vulnerabilities in safe code (e.g., out-of-bounds write or read). Code that does not manually implement Error::type_id is unaffected.

## References
- https://groups.google.com/forum/#%21topic/rustlang-security-announcements/aZabeCMUv70
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HG47HYH3AQTUMBUMX3S3G5DNAY4CBW6N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K6T4BNA5KQYJRIKIGGBOGBMR7TRXPHLR/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00076.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00031.html
- https://blog.rust-lang.org/2019/05/13/Security-advisory.html
