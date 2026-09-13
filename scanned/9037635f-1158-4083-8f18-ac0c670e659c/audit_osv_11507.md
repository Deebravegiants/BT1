# [H] CVE-2017-8284

## Summary
Severity: High
Advisory: CVE-2017-8284
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-26
Source: https://osv.dev/vulnerability/CVE-2017-8284
Type: osv

## Details
The disas_insn function in target/i386/translate.c in QEMU before 2.9.0, when TCG mode without hardware acceleration is used, does not limit the instruction size, which allows local users to gain privileges by creating a modified basic block that injects code into a setuid program, as demonstrated by procmail. NOTE: the vendor has stated "this bug does not violate any security guarantees QEMU makes.

## References
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1122
- https://github.com/qemu/qemu/commit/30663fd26c0307e414622c7a8607fbc04f92ec14
