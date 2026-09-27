# [H] CVE-2024-4981

## Summary
Severity: High
Advisory: CVE-2024-4981
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-05-12
Source: https://osv.dev/vulnerability/CVE-2024-4981
Type: osv

## Details
A vulnerability was discovered in Pagure server. If a malicious user were to submit a git repository with symbolic links, the server could unintentionally show incorporate and make visible content from outside the git repo.

## References
- https://access.redhat.com/security/cve/CVE-2024-4981
- https://bugzilla.redhat.com/show_bug.cgi?id=2278745
- https://bugzilla.redhat.com/show_bug.cgi?id=2280723
- https://pagure.io/pagure/c/454f2677bc50d7176f07da9784882eb2176537f4
