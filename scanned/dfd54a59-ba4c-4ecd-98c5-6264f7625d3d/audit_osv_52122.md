# [H] CVE-2021-47098

## Summary
Severity: High
Advisory: CVE-2021-47098
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47098
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

hwmon: (lm90) Prevent integer overflow/underflow in hysteresis calculations

Commit b50aa49638c7 ("hwmon: (lm90) Prevent integer underflows of
temperature calculations") addressed a number of underflow situations
when writing temperature limits. However, it missed one situation, seen
when an attempt is made to set the hysteresis value to MAX_LONG and the
critical temperature limit is negative.

Use clamp_val() when setting the hysteresis temperature to ensure that
the provided value can never overflow or underflow.

## References
- https://git.kernel.org/stable/c/55840b9eae5367b5d5b29619dc2fb7e4596dba46
- https://git.kernel.org/stable/c/d105f30bea9104c590a9e5b495cb8a49bdfe405f
