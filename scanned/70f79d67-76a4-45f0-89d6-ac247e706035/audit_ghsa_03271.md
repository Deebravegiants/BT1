# [H] cumulative-distribution-function Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-58qp-5328-v7mh
CVE: CVE-2021-29486
CWE: CWE-20, CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-04
Source: https://github.com/advisories/GHSA-58qp-5328-v7mh
Type: github-advisory

## Affected
- npm: `cumulative-distribution-function` — affected >=0 <2.0.0

## Details
### Impact

* Apps using this library on improper data may crash or go into an infinite-loop
* In the case of a nodejs server-app using this library to act on invalid non-numeric data, the nodejs server may crash.  This may affect other users of this server and/or require the server to be rebooted for proper operation.  
* In the case of a browser app using this library to act on invalid non-numeric data, that browser may crash or lock up.

A flaw enabling an infinite-loop was discovered in the code for evaluating the cumulative-distribution-function
of input data.   Although the documentation explains that numeric data is required, some users may confuse an array
of strings like ["1","2","3","4","5"] for numeric data [1,2,3,4,5] when it is in fact string data.  An infinite loop is possible when the 
cumulative-distribution-function  is evaluated for a given point when the input data is string data rather than type `number`.  

This vulnerability enables an infinite-cpu-loop denial-of-service-attack on any app using npm:cumulative-distribution-function v1.0.3 or earlier if the attacker can supply malformed data to the library.  The vulnerability could also manifest if a data source to
be analyzed changes data type from Arrays of number (proper) to Arrays of string (invalid, but undetected by earlier version of the library).

### Patches

Users should upgrade to at least v2.0.0, or the latest version.

Tests for several types of invalid data have been created, and version 2.0.0 has been tested to reject this invalid data by
throwing a `TypeError()` instead of processing it.  Developers using this library may wish to adjust their app's code slightly to better tolerate or handle this TypeError.  Apps performing proper numeric data validation before sending data to this library should be mostly unaffected by this patch.  

### Workarounds

The vulnerability can be mitigated in older versions by ensuring that only finite numeric data of type `Array[number]` or `number` is passed to `cumulative-distribution-function` and its `f(x)` function, respectively.  

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the Github repository at https://github.com/DrPaulBrewer/cumulative-distribution-function

## References
- https://github.com/DrPaulBrewer/cumulative-distribution-function/security/advisories/GHSA-58qp-5328-v7mh
- https://nvd.nist.gov/vuln/detail/CVE-2021-29486
- https://github.com/DrPaulBrewer/cumulative-distribution-function/issues/7
- https://github.com/DrPaulBrewer/cumulative-distribution-function/pull/8
- https://www.npmjs.com/package/cumulative-distribution-function
