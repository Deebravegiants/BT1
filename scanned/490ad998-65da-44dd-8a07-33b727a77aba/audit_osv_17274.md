# [H] CVE-2020-14298

## Summary
Severity: High
Advisory: CVE-2020-14298
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-07-13
Source: https://osv.dev/vulnerability/CVE-2020-14298
Type: osv

## Details
The version of docker as released for Red Hat Enterprise Linux 7 Extras via RHBA-2020:0053 advisory included an incorrect version of runc missing the fix for CVE-2019-5736, which was previously fixed via RHSA-2019:0304. This issue could allow a malicious or compromised container to compromise the container host and other containers running on the same host. This issue only affects docker version 1.13.1-108.git4ef4b30.el7, shipped in Red Hat Enterprise Linux 7 Extras. Both earlier and later versions are not affected.

## References
- https://access.redhat.com/errata/RHBA-2020:0427
- https://access.redhat.com/security/cve/CVE-2020-14298
- https://access.redhat.com/security/vulnerabilities/runcescape
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-5736
