# [H] NULL Pointer Dereference in mrb_vm_exec with super in mruby/mruby

## Summary
Severity: High
Advisory: CVE-2022-1201
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-04-02
Source: https://osv.dev/vulnerability/CVE-2022-1201
Type: osv

## Details
NULL Pointer Dereference in mrb_vm_exec with super in GitHub repository mruby/mruby prior to 3.2. This vulnerability is capable of making the mruby interpreter crash, thus affecting the availability of the system.

## References
- https://huntr.dev/bounties/6f930add-c9d8-4870-ae56-d4bd8354703b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1201.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1201
- https://github.com/mruby/mruby/commit/00acae117da1b45b318dc36531a7b0021b8097ae
