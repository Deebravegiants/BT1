# [H] Symbolic Link (Symlink) Following in github.com/pterodactyl/wings

## Summary
Severity: High
Advisory: CVE-2023-25152
Aliases: GHSA-p8r3-83r8-jwj5, GO-2023-1542
CVSS: 8.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:H)
Published: 2023-02-08
Source: https://osv.dev/vulnerability/CVE-2023-25152
Type: osv

## Details
Wings is Pterodactyl's server control plane. Affected versions are subject to a vulnerability which can be used to create new files and directory structures on the host system that previously did not exist, potentially allowing attackers to change their resource allocations, promote their containers to privileged mode, or potentially add ssh authorized keys to allow the attacker access to a remote shell on the target machine.   In order to use this exploit, an attacker must have an existing "server" allocated and controlled by the Wings Daemon. This vulnerability has been resolved in version `v1.11.3` of the Wings Daemon, and has been back-ported to the 1.7 release series in `v1.7.3`. Anyone running `v1.11.x` should upgrade to `v1.11.3` and anyone running `v1.7.x` should upgrade to `v1.7.3`. There are no known workarounds for this vulnerability.

### Workarounds

None at this time.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25152.json
- https://github.com/pterodactyl/wings/security/advisories/GHSA-p8r3-83r8-jwj5
- https://nvd.nist.gov/vuln/detail/CVE-2023-25152
- https://github.com/pterodactyl/wings/commit/dac9685298c3c1c49b3109fa4241aa88272b9f14
