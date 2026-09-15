# [H] CVE-2018-17293

## Summary
Severity: High
Advisory: CVE-2018-17293
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-21
Source: https://osv.dev/vulnerability/CVE-2018-17293
Type: osv

## Details
An issue was discovered in WAVM before 2018-09-16. The run function in Programs/wavm/wavm.cpp does not check whether there is Emscripten memory to store the command-line arguments passed by the input WebAssembly file's main function, which allows attackers to cause a denial of service (application crash by NULL pointer dereference) or possibly have unspecified other impact by crafting certain WebAssembly files.

## References
- https://github.com/WAVM/WAVM/commit/31d670b6489e6d708c3b04b911cdf14ac43d846d
- https://github.com/WAVM/WAVM/issues/110#issuecomment-421764693
