# [C] CVE-2019-1010176

## Summary
Severity: Critical
Advisory: CVE-2019-1010176
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-25
Source: https://osv.dev/vulnerability/CVE-2019-1010176
Type: osv

## Details
JerryScript commit 4e58ccf68070671e1fff5cd6673f0c1d5b80b166 is affected by: Buffer Overflow. The impact is: denial of service and possibly arbitrary code execution. The component is: function lit_char_to_utf8_bytes (jerry-core/lit/lit-char-helpers.c:377). The attack vector is: executing crafted javascript code. The fixed version is: after commit 505dace719aebb3308a3af223cfaa985159efae0.

## References
- https://github.com/jerryscript-project/jerryscript/issues/2476
