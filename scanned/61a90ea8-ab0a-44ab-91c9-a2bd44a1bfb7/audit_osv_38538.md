# [C] Creolabs Gravity < 0.9.6 Heap Buffer Overflow via gravity_vm_exec

## Summary
Severity: Critical
Advisory: CVE-2026-40504
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40504
Type: osv

## Details
Creolabs Gravity before 0.9.6 contains a heap buffer overflow vulnerability in the gravity_vm_exec function that allows attackers to write out-of-bounds memory by crafting scripts with many string literals at global scope. Attackers can exploit insufficient bounds checking in gravity_fiber_reassign() to corrupt heap metadata and achieve arbitrary code execution in applications that evaluate untrusted scripts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40504.json
- https://github.com/marcobambini/gravity/releases/tag/0.9.6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40504
- https://www.vulncheck.com/advisories/creolabs-gravity-heap-buffer-overflow-via-gravity-vm-exec
- https://github.com/marcobambini/gravity/issues/437
- https://github.com/marcobambini/gravity/commit/18b9195598d9b944376754c6d1ad76e38a4adca1
- https://github.com/marcobambini/gravity
