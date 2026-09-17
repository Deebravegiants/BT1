# [H] Ansible FreeBSD Jail Connection Plugin: Jail escape via symlink following in put_file (host-side root mv)

## Summary
Severity: High
Advisory: GHSA-cxgv-hp74-jj7r
CVE: CVE-2026-55074
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-cxgv-hp74-jj7r
Type: github-advisory

## Affected
- PyPI: `ansible-jailexec` — affected >=0 <2.0.0

## Details
Through version 1.3.0, the jailexec connection plugin's put_file resolved a transfer's destination to a path on the jail host (<jail filesystem root> + <destination>) and ran mkdir -p and mv there as root on the host. Those commands follow symbolic links, and the path was operated on outside the jail, so a symlink existing inside the jail was followed by the host-side, root-privileged mv.

A party controlling content inside a managed jail (the jail's root, or any process able to create a symlink in a directory an Ansible task later writes to) can therefore cause an arbitrary root-owned write on the host, outside the jail — a full jail escape. Arbitrary root-owned host writes are readily escalated to host compromise (e.g. cron, rc.d, authorized_keys).

Preconditions: the operator runs a copy/template/fetch-style task (anything using put_file) against the jail, and the attacker can place a symlink inside the jail at or above the task's destination before the transfer runs.

Patches: Fixed in 2.0.0. File transfers now run inside the jail via jexec (mkdir -p <dir> && cat > <dest> for put_file; cat < <src> for fetch_file), so every path resolves within the jail's chroot. An in-jail symlink can at most redirect within the same jail and can no longer reach the host.

Workarounds: None in affected versions; upgrade to 2.0.0.

## References
- https://github.com/chofstede/ansible_jailexec/security/advisories/GHSA-cxgv-hp74-jj7r
- https://github.com/chofstede/ansible_jailexec/commit/6e80eecb2db7aebd1258fded6ae5c3aba1dd4123
- https://github.com/chofstede/ansible_jailexec
