# [H] btrfs: always report error in run_one_delayed_ref()

## Summary
Severity: High
Advisory: CVE-2022-49761
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49761
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.165, >=5.11.0 <5.15.90, >=5.16.0 <6.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: always report error in run_one_delayed_ref()

Currently we have a btrfs_debug() for run_one_delayed_ref() failure, but
if end users hit such problem, there will be no chance that
btrfs_debug() is enabled.  This can lead to very little useful info for
debugging.

This patch will:

- Add extra info for error reporting
  Including:
  * logical bytenr
  * num_bytes
  * type
  * action
  * ref_mod

- Replace the btrfs_debug() with btrfs_err()

- Move the error reporting into run_one_delayed_ref()
  This is to avoid use-after-free, the @node can be freed in the caller.

This error should only be triggered at most once.

As if run_one_delayed_ref() failed, we trigger the error message, then
causing the call chain to error out:

btrfs_run_delayed_refs()
`- btrfs_run_delayed_refs()
   `- btrfs_run_delayed_refs_for_head()
      `- run_one_delayed_ref()

And we will abort the current transaction in btrfs_run_delayed_refs().
If we have to run delayed refs for the abort transaction,
run_one_delayed_ref() will just cleanup the refs and do nothing, thus no
new error messages would be output.

## References
- https://git.kernel.org/stable/c/18bd1c9c02e64a3567f90c83c2c8b855531c8098
- https://git.kernel.org/stable/c/39f501d68ec1ed5cd5c66ac6ec2a7131c517bb92
- https://git.kernel.org/stable/c/853ffa1511b058c79a4c9bb1407b3b20ce311792
- https://git.kernel.org/stable/c/fdb4a70bb768d2a87890409597529ad81cb3de8a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49761.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49761
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
