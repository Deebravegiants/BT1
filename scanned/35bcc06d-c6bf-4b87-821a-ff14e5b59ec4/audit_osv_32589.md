# [H] Conda-build Insecure Build Script Permissions Enabling Arbitrary Code Execution

## Summary
Severity: High
Advisory: CVE-2025-32797
Aliases: GHSA-vfp6-3v8g-vcmm
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-32797
Type: osv

## Details
Conda-build contains commands and tools to build conda packages. Prior to version 25.3.1, the write_build_scripts function in conda-build creates the temporary build script conda_build.sh with overly permissive file permissions (0o766), allowing write access to all users. Attackers with filesystem access can exploit a race condition to overwrite the script before execution, enabling arbitrary code execution under the victim's privileges. This risk is significant in shared environments, potentially leading to full system compromise. Even with non-static directory names, attackers can monitor parent directories for file creation events. The brief window between script creation (with insecure permissions) and execution allows rapid overwrites. Directory names can also be inferred via timestamps or logs, and automation enables exploitation even with semi-randomized paths by acting within milliseconds of detection. This issue has been patched in version 25.3.1. A workaround involves restricting conda_build.sh permissions from 0o766 to 0o700 (owner-only read/write/execute). Additionally, use atomic file creation (write to a temporary randomized filename and rename atomically) to minimize the race condition window.

## References
- https://github.com/conda/conda-build/blob/3f06913bba22c4e1ef1065df9e00d86ac97f087c/conda_build/build.py#L3054-L3084
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32797.json
- https://github.com/conda/conda-build/security/advisories/GHSA-vfp6-3v8g-vcmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-32797
- https://github.com/conda/conda-build/commit/d246e49c8f45e8033915156ee3d77769926f3c2e
- https://github.com/conda/conda-build/pull/5
