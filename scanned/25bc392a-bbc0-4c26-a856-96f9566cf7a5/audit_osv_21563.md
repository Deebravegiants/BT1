# [H] CVE-2021-44078

## Summary
Severity: High
Advisory: CVE-2021-44078
Aliases: PYSEC-2021-868
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-12-26
Source: https://osv.dev/vulnerability/CVE-2021-44078
Type: osv

## Details
An issue was discovered in split_region in uc.c in Unicorn Engine before 2.0.0-rc5. It allows local attackers to escape the sandbox. An attacker must first obtain the ability to execute crafted code in the target sandbox in order to exploit this vulnerability. The specific flaw exists within the virtual memory manager. The issue results from the faulty comparison of GVA and GPA while calling uc_mem_map_ptr to free part of a claimed memory block. An attacker can leverage this vulnerability to escape the sandbox and execute arbitrary code on the host machine.

## References
- https://gist.github.com/jwang-a/cb4b6e9551457aa299066076b836a2cd
- https://github.com/jwang-a/CTF/blob/master/MyChallenges/Pwn/Unicorns_Aisle/UnicornsAisle.pdf
- https://www.unicorn-engine.org/changelog/
- https://github.com/unicorn-engine/unicorn/commit/c733bbada356b0373fa8aa72c044574bb855fd24
- https://github.com/unicorn-engine/unicorn/compare/2.0.0-rc4...2.0.0-rc5
