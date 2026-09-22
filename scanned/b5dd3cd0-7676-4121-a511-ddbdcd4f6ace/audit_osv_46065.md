# [H] JLSEC-2026-64

## Summary
Severity: High
Advisory: JLSEC-2026-64
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/JLSEC-2026-64
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=8.9.0+0 <9.1.0+0

## Details
ssh-agent in OpenSSH before 8.5 has a double free that may be relevant in a few less-common scenarios, such as unconstrained agent-socket access on a legacy operating system, or the forwarding of an agent to an attacker-controlled host.

## References
- https://github.com/openssh/openssh-portable/commit/e04fd6dde16de1cdc5a4d9946397ff60d96568db
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQWGII3LQR4AOTPPFXGMTYE7UDEWIUKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TXST2CML2MWY3PNVUXX7FFJE3ATJMNVZ/
- https://security.gentoo.org/glsa/202105-35
- https://security.netapp.com/advisory/ntap-20210416-0002/
- https://www.openssh.com/security.html
- https://www.openssh.com/txt/release-8.5
- https://www.openwall.com/lists/oss-security/2021/03/03/1
- https://www.oracle.com//security-alerts/cpujul2021.html
