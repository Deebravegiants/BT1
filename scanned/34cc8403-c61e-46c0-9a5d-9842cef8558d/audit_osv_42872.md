# [H] cpu: hotplug: Preserve per instance callback errors

## Summary
Severity: High
Advisory: CVE-2026-72067
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72067
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpu: hotplug: Preserve per instance callback errors

cpuhp_invoke_callback() unwinds earlier callbacks for the same
hotplug state when one instance fails. The rollback path currently
reuses ret, so a successful rollback can hide the original error and
make the failed transition look successful.

Keep the rollback result separate from the original error.

## References
- https://git.kernel.org/stable/c/673db10729fb121ea1b16fe57791a0cb9eac1eb5
- https://git.kernel.org/stable/c/77d4fa8a3ea1c3e8b996ac35e59aee9e77389905
- https://git.kernel.org/stable/c/7a68257b90d8a9b6d605abc99469ded45ecba63b
- https://git.kernel.org/stable/c/95232281512b15338549171ed9a2acf21f946ffb
- https://git.kernel.org/stable/c/9f7dc355f62c011e4afe8286cf71130d4bfb9d80
- https://git.kernel.org/stable/c/ef39758637cc5b603fb05b625c45a98aa306e338
- https://git.kernel.org/stable/c/f77117530fc3f5932ffb107182a6dd34006be9b6
- https://git.kernel.org/stable/c/fe9c8d641f6991614d1229a3ffd3e33b879bba9c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72067.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72067
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
