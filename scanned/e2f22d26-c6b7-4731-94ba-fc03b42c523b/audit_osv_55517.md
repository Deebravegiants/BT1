# [H] CVE-2025-62496

## Summary
Severity: High
Advisory: CVE-2025-62496
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-62496
Type: osv

## Details
A vulnerability exists in the QuickJS engine's BigInt string parsing logic (js_bigint_from_string) when attempting to create a BigInt from a string with an excessively large number of digits.

The function calculates the necessary number of bits (n_bits) required to store the BigInt using the formula:

$$\text{n\_bits} = (\text{n\_digits} \times 27 + 7) / 8 \quad (\text{for radix 10})$$

  *  For large input strings (e.g., $79,536,432$ digits or more for base 10), the intermediate calculation $(\text{n\_digits} \times 27 + 7)$ exceeds the maximum value of a standard signed 32-bit integer, resulting in an Integer Overflow.


  *  The resulting n_bits value becomes unexpectedly small or even negative due to this wrap-around.


  *  This flawed n_bits is then used to compute n_limbs, the number of memory "limbs" needed for the BigInt object. Since n_bits is too small, the calculated n_limbs is also significantly underestimated.


  *  The function proceeds to allocate a JSBigInt object using this underestimated n_limbs.


  *  When the function later attempts to write the actual BigInt data into the allocated object, the small buffer size is quickly exceeded, leading to a Heap Out-of-Bounds Write as data is written past the end of the allocated r->tab array.

## References
- https://bellard.org/quickjs/Changelog
- https://issuetracker.google.com/434193016
