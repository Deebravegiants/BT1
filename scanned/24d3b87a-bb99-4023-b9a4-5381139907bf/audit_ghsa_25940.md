# [H] Use of insecure temporary file in Horovod

## Summary
Severity: High
Advisory: GHSA-47wv-vhj2-g66m
CVE: CVE-2022-0315
CWE: CWE-377, CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2022-03-29
Source: https://github.com/advisories/GHSA-47wv-vhj2-g66m
Type: github-advisory

## Affected
- PyPI: `horovod` — affected >=0 <0.24.0

## Details
### Impact
The insecure `tempfile.mktemp()` is used when Horovod is run in an LSF job with `jsrun`. In that situation, a jsrun rank file is created with `mktemp`, which could be hijacked by another process to read or manipulate the content.

This issue does not impact the use of MPI, Gloo, Spark or Ray.

### Patches
The problem has been fixed in [b96ecae4](https://github.com/horovod/horovod/commit/b96ecae4dc69fc0a83c7c2d3f1dde600c20a1b41).

### Workarounds
The rank file is not created when `binding_args` are provided in the `Settings` instance.

### References
Please see https://github.com/horovod/horovod/pull/3358 for details.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/horovod/horovod](https://github.com/horovod/horovod/issues/new/choose)

## References
- https://github.com/horovod/horovod/security/advisories/GHSA-47wv-vhj2-g66m
- https://nvd.nist.gov/vuln/detail/CVE-2022-0315
- https://github.com/horovod/horovod/pull/3358
- https://github.com/horovod/horovod/commit/b96ecae4dc69fc0a83c7c2d3f1dde600c20a1b41
- https://github.com/advisories/GHSA-47wv-vhj2-g66m
- https://github.com/horovod/horovod
- https://github.com/pypa/advisory-database/tree/main/vulns/horovod/PYSEC-2022-175.yaml
- https://huntr.dev/bounties/7e50397b-dd63-4bb5-b56d-704094a7da45
