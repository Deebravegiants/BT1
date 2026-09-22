# [M] CVE-2021-4115

## Summary
Severity: Medium
Advisory: CVE-2021-4115
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/CVE-2021-4115
Type: osv

## Details
There is a flaw in polkit which can allow an unprivileged user to cause polkit to crash, due to process file descriptor exhaustion. The highest threat from this vulnerability is to availability. NOTE: Polkit process outage duration is tied to the failing process being reaped and a new one being spawned

## References
- http://packetstormsecurity.com/files/172849/polkit-File-Descriptor-Exhaustion.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VGKWCBS6IDZYYDYM2WIWJM5BL7QQTWPF/
- https://access.redhat.com/security/cve/cve-2021-4115
- https://gitlab.com/redhat/centos-stream/rpms/polkit/-/merge_requests/6/diffs?commit_id=bf900df04dc390d389e59aa10942b0f2b15c531e
- https://gitlab.freedesktop.org/polkit/polkit/-/issues/141
- https://www.oracle.com/security-alerts/cpujul2022.html
