# [M] CVE-2025-62492

## Summary
Severity: Medium
Advisory: CVE-2025-62492
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62492
Type: osv

## Details
A vulnerability stemming from floating-point arithmetic precision errors exists in the QuickJS engine's implementation of TypedArray.prototype.indexOf() when a negative fromIndex argument is supplied.

  *  The fromIndex argument (read as a double variable, $d$) is used to calculate the starting position for the search.


  *  If d is negative, the index is calculated relative to the end of the array by adding the array's length (len) to d:



$$d_{new} = d + \text{len}$$


  *  Due to the inherent limitations of floating-point arithmetic, if the negative value $d$ is extremely small (e.g., $-1 \times 10^{-20}$), the addition $d + \text{len}$ can result in a loss of precision, yielding an outcome that is exactly equal to $\text{len}$.


  *  The result is then converted to an integer index $k$: $k = \text{len}$.


  *  The search function proceeds to read array elements starting from index $k$. Since valid indices are $0$ to $\text{len}-1$, starting the read at index $\text{len}$ is one element past the end of the array.


This allows an attacker to cause an Out-of-Bounds Read of one element immediately following the buffer. While the scope of this read is small (one element), it can potentially lead to Information Disclosure of adjacent memory contents, depending on the execution environment.

## References
- https://bellard.org/quickjs/Changelog
- https://issuetracker.google.com/434194797
