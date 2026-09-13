# [M] Apptainer ineffectively applies selinux and apparmor --security options

## Summary
Severity: Medium
Advisory: GHSA-j3rw-fx6g-q46j
CVE: CVE-2025-65105
CWE: CWE-61, CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-j3rw-fx6g-q46j
Type: github-advisory

## Affected
- Go: `github.com/apptainer/apptainer` — affected >=0 <1.4.5

## Details
### Impact
In Apptainer versions less than 1.4.5, a container can disable two of the forms of the little used `--security` option, in particular the forms `--security=apparmor:<profile>` and `--security=selinux:<label>` which otherwise put restrictions on operations that containers can do.  The `--security` option has always been mentioned in Apptainer documentation as being a feature for the root user, although these forms do also work for unprivileged users on systems where the corresponding feature is enabled.  Apparmor is enabled by default on Debian-based distributions and SElinux is enabled by default on RHEL-based distributions, but on SUSE it depends on the distribution version.

In addition, a bug in the detection of selinux support in Apptainer's suid mode means that `--security selinux:<label>` flags may not be applied, even in the absence of an attack.  In that case a warning message is emitted indicating that selinux is unavailable, but the warning may be may be overlooked, mis-interpreted, or not seen when apptainer is run from a script or other tool.  Failure to apply requested restrictions should result in a fatal error rather than just a warning message.

### Patches
Ineffective write of selinux process labels is addressed via an update to the containers/selinux dependency in https://github.com/apptainer/apptainer/pull/3226. That update brings in the upstream fix for https://github.com/advisories/GHSA-cgrx-mc8f-2prm which was for a different but related vulnerability.

Ineffective write of apparmor process profiles is addressed in commit 4313b42.

Failure to detect apparmor / selinux support, when --security flags are provided, is made an error rather than a warning in commit 82f1790.

### Workarounds
There are no known workarounds, other than to define system-wide apparmor / selinux policy for Apptainer itself. This would apply to all containers, not just those run with the `--security` flags, and could impact the operation of Apptainer itself.

### References
Thanks to Sylabs for finding this issue, fixing it in https://github.com/sylabs/singularity/security/advisories/GHSA-wwrx-w7c9-rf87 which was easy to import into Apptainer, and disclosing it early to the Apptainer project for a coordinated release.

The related upstream runc disclosure which inspired the investigation is https://github.com/opencontainers/runc/security/advisories/GHSA-cgrx-mc8f-2prm.

## References
- https://github.com/apptainer/apptainer/security/advisories/GHSA-j3rw-fx6g-q46j
- https://github.com/opencontainers/runc/security/advisories/GHSA-cgrx-mc8f-2prm
- https://github.com/sylabs/singularity/security/advisories/GHSA-wwrx-w7c9-rf87
- https://nvd.nist.gov/vuln/detail/CVE-2025-65105
- https://github.com/apptainer/apptainer/pull/3226
- https://github.com/apptainer/apptainer/commit/4313b42717e18a4add7dd7503528bc15af905981
- https://github.com/apptainer/apptainer/commit/82f17900a0c31bc769bf9b4612d271c7068d8bf2
- https://github.com/apptainer/apptainer
