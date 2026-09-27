# [H] CVE-2021-28041

## Summary
Severity: High
Advisory: CVE-2021-28041
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-05
Source: https://osv.dev/vulnerability/CVE-2021-28041
Type: osv

## Details
ssh-agent in OpenSSH before 8.5 has a double free that may be relevant in a few less-common scenarios, such as unconstrained agent-socket access on a legacy operating system, or the forwarding of an agent to an attacker-controlled host.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQWGII3LQR4AOTPPFXGMTYE7UDEWIUKI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TXST2CML2MWY3PNVUXX7FFJE3ATJMNVZ/
- https://security.gentoo.org/glsa/202105-35
- https://security.netapp.com/advisory/ntap-20210416-0002/
- https://www.openssh.com/security.html
- https://www.openssh.com/txt/release-8.5
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://github.com/openssh/openssh-portable/commit/e04fd6dde16de1cdc5a4d9946397ff60d96568db
- https://www.openwall.com/lists/oss-security/2021/03/03/1
