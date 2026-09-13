# [M] CVE-2021-45942

## Summary
Severity: Medium
Advisory: CVE-2021-45942
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45942
Type: osv

## Details
OpenEXR 3.1.x before 3.1.4 has a heap-based buffer overflow in Imf_3_1::LineCompositeTask::execute (called from IlmThread_3_1::NullThreadPoolProvider::addTask and IlmThread_3_1::ThreadPool::addGlobalTask). NOTE: db217f2 may be inapplicable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6TEZDE2S2DB4BF4LZSSV4W3DNW7DSRHJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HJ5PW4WNXBKCRFGDZGAQOSVH2BKZKL4X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XJUK7WIQV5EKWTCZBRXFN6INHG6MLS5O/
- https://github.com/AcademySoftwareFoundation/openexr/blob/v3.1.4/CHANGES.md#version-314-january-26-2022
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.1.4
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/openexr/OSV-2021-1627.yaml
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=41416
- https://github.com/AcademySoftwareFoundation/openexr/commit/11cad77da87c4fa2aab7d58dd5339e254db7937e
- https://github.com/AcademySoftwareFoundation/openexr/commit/db217f29dfb24f6b4b5100c24ac5e7490e1c57d0
- https://github.com/AcademySoftwareFoundation/openexr/pull/1209
