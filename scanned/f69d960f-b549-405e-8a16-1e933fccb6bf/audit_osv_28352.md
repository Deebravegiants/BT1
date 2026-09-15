# [M] CVE-2024-31852

## Summary
Severity: Medium
Advisory: CVE-2024-31852
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-05
Source: https://osv.dev/vulnerability/CVE-2024-31852
Type: osv

## Details
LLVM before 18.1.3 generates code in which the LR register can be overwritten without data being saved to the stack, and thus there can sometimes be an exploitable error in the flow of control. This affects the ARM backend and can be demonstrated with Clang. NOTE: the vendor perspective is "we don't have strong objections for a CVE to be created ... It does seem that the likelihood of this miscompile enabling an exploit remains very low, because the miscompile resulting in this JOP gadget is such that the function is most likely to crash on most valid inputs to the function. So, if this function is covered by any testing, the miscompile is most likely to be discovered before the binary is shipped to production."

## References
- https://bugs.chromium.org/p/llvm/issues/detail?id=69
- https://llvm.org/docs/Security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31852.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-31852
- https://github.com/llvm/llvm-project/issues/80287
- https://github.com/llvmbot/llvm-project/commit/0e16af8e4cf3a66ad5d078d52744ae2776f9c4b2
