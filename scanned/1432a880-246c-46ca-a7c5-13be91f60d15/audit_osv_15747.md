# [C] CVE-2019-19333

## Summary
Severity: Critical
Advisory: CVE-2019-19333
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-06
Source: https://osv.dev/vulnerability/CVE-2019-19333
Type: osv

## Details
In all versions of libyang before 1.0-r5, a stack-based buffer overflow was discovered in the way libyang parses YANG files with a leaf of type "bits". An application that uses libyang to parse untrusted YANG files may be vulnerable to this flaw, which would allow an attacker to cause a denial of service or possibly gain code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PETB6TVMFV5KUD4IKVP2JPLBCYHUGSAJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RL54JMS7XW7PI6JC4BFSNNLSX5AINQUL/
- https://access.redhat.com/errata/RHSA-2019:4360
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-19333
- https://github.com/CESNET/libyang/commit/f6d684ade99dd37b21babaa8a856f64faa1e2e0d
