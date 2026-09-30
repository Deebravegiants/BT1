# [H] crypto: qce - fix error path in devm_qce_register_algs

## Summary
Severity: High
Advisory: CVE-2026-80565
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80565
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.14.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qce - fix error path in devm_qce_register_algs

If ops->register_algs() fails, the error path repeatedly calls the same
ops->unregister_algs() from the failed registration. Use the loop index
to unregister the previously registered algorithms instead.

## References
- https://git.kernel.org/stable/c/1ece8e16c085e8cd60ecbdb641269aaa53d31da4
- https://git.kernel.org/stable/c/4e88b4fda48282f3fd504b4d4f5d2d4f996b76ce
- https://git.kernel.org/stable/c/9c75402286409f5e1a75e4a445555c84066f89db
- https://git.kernel.org/stable/c/a134e4b8102c077286818ee112b9f925db613d4c
- https://git.kernel.org/stable/c/c7dc487aade12c692add3221673c9bdf32dc24f5
- https://git.kernel.org/stable/c/dbca8b798caf47fb2799a26dd09c9ad66305883d
- https://git.kernel.org/stable/c/de52c713d21806b93b00a6074056b57aec4f8919
- https://git.kernel.org/stable/c/fef187c6194d67395182d58169dd14ba631f1b41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80565.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80565
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
