# [H] CVE-2025-62494

## Summary
Severity: High
Advisory: CVE-2025-62494
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62494
Type: osv

## Details
A type confusion vulnerability exists in the handling of the string addition (+) operation within the QuickJS engine.

  *  The code first checks if the left-hand operand is a string.


  *  It then attempts to convert the right-hand operand to a primitive value using JS_ToPrimitiveFree. This conversion can trigger a callback (e.g., toString or valueOf).


  *  During this callback, an attacker can modify the type of the left-hand operand in memory, changing it from a string to a different type (e.g., an object or an array).


  *  The code then proceeds to call JS_ConcatStringInPlace, which still treats the modified left-hand value as a string.


This mismatch between the assumed type (string) and the actual type allows an attacker to control the data structure being processed by the concatenation logic, resulting in a type confusion condition. This can lead to out-of-bounds memory access, potentially resulting in memory corruption and arbitrary code execution in the context of the QuickJS runtime.

## References
- https://bellard.org/quickjs/Changelog
- https://issuetracker.google.com/434193023
