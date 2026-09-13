# [M] CVE-2024-48936

## Summary
Severity: Medium
Advisory: CVE-2024-48936
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-28
Source: https://osv.dev/vulnerability/CVE-2024-48936
Type: osv

## Details
SchedMD Slurm before 24.05.4 has Incorrect Authorization. A mistake in authentication handling in stepmgr could permit an attacker to execute processes under other users' jobs. This is limited to jobs explicitly running with --stepmgr, or on systems that have globally enabled stepmgr via SlurmctldParameters=enable_stepmgr in their configuration.

## References
- https://lists.schedmd.com/mailman3/hyperkitty/list/slurm-announce%40lists.schedmd.com/message/44MFMN7R35YZFWTNO43R2754W5B5XUAI/
- https://lists.schedmd.com/pipermail/slurm-announce/2024/date.html
- https://www.schedmd.com/security-policy/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48936.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48936
