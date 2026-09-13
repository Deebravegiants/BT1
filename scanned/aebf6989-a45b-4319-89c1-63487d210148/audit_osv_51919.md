# [C] CVE-2021-45423

## Summary
Severity: Critical
Advisory: CVE-2021-45423
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-13
Source: https://osv.dev/vulnerability/CVE-2021-45423
Type: osv

## Details
A Buffer Overflow vulnerabilityexists in Pev 0.81 via the pe_exports function from exports.c.. The array offsets_to_Names is dynamically allocated on the stack using exp->NumberOfFunctions as its size. However, the loop uses exp->NumberOfNames to iterate over it and set its components value. Therefore, the loop code assumes that exp->NumberOfFunctions is greater than ordinal at each iteration. This can lead to arbitrary code execution.

## References
- https://github.com/merces/libpe/issues/35
