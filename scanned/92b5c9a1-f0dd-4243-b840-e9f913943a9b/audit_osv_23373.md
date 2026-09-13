# [H] crypto: qcom-rng - ensure buffer for generate is completely filled

## Summary
Severity: High
Advisory: CVE-2022-48629
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-05
Source: https://osv.dev/vulnerability/CVE-2022-48629
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.236, >=4.20.0 <5.4.187, >=5.5.0 <5.10.108, >=5.11.0 <5.15.31, >=5.16.0 <5.16.17

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qcom-rng - ensure buffer for generate is completely filled

The generate function in struct rng_alg expects that the destination
buffer is completely filled if the function returns 0. qcom_rng_read()
can run into a situation where the buffer is partially filled with
randomness and the remaining part of the buffer is zeroed since
qcom_rng_generate() doesn't check the return value. This issue can
be reproduced by running the following from libkcapi:

    kcapi-rng -b 9000000 > OUTFILE

The generated OUTFILE will have three huge sections that contain all
zeros, and this is caused by the code where the test
'val & PRNG_STATUS_DATA_AVAIL' fails.

Let's fix this issue by ensuring that qcom_rng_read() always returns
with a full buffer if the function returns success. Let's also have
qcom_rng_generate() return the correct value.

Here's some statistics from the ent project
(https://www.fourmilab.ch/random/) that shows information about the
quality of the generated numbers:

    $ ent -c qcom-random-before
    Value Char Occurrences Fraction
      0           606748   0.067416
      1            33104   0.003678
      2            33001   0.003667
    ...
    253   �        32883   0.003654
    254   �        33035   0.003671
    255   �        33239   0.003693

    Total:       9000000   1.000000

    Entropy = 7.811590 bits per byte.

    Optimum compression would reduce the size
    of this 9000000 byte file by 2 percent.

    Chi square distribution for 9000000 samples is 9329962.81, and
    randomly would exceed this value less than 0.01 percent of the
    times.

    Arithmetic mean value of data bytes is 119.3731 (127.5 = random).
    Monte Carlo value for Pi is 3.197293333 (error 1.77 percent).
    Serial correlation coefficient is 0.159130 (totally uncorrelated =
    0.0).

Without this patch, the results of the chi-square test is 0.01%, and
the numbers are certainly not random according to ent's project page.
The results improve with this patch:

    $ ent -c qcom-random-after
    Value Char Occurrences Fraction
      0            35432   0.003937
      1            35127   0.003903
      2            35424   0.003936
    ...
    253   �        35201   0.003911
    254   �        34835   0.003871
    255   �        35368   0.003930

    Total:       9000000   1.000000

    Entropy = 7.999979 bits per byte.

    Optimum compression would reduce the size
    of this 9000000 byte file by 0 percent.

    Chi square distribution for 9000000 samples is 258.77, and randomly
    would exceed this value 42.24 percent of the times.

    Arithmetic mean value of data bytes is 127.5006 (127.5 = random).
    Monte Carlo value for Pi is 3.141277333 (error 0.01 percent).
    Serial correlation coefficient is 0.000468 (totally uncorrelated =
    0.0).

This change was tested on a Nexus 5 phone (msm8974 SoC).

## References
- https://git.kernel.org/stable/c/0f9b7b8df17525e464294c916acc8194ce38446b
- https://git.kernel.org/stable/c/184f7bd08ce56f003530fc19f160d54e75bf5c9d
- https://git.kernel.org/stable/c/485995cbc98a4f77cfd4f8ed4dd7ff8ab262964d
- https://git.kernel.org/stable/c/a680b1832ced3b5fa7c93484248fd221ea0d614b
- https://git.kernel.org/stable/c/a8e32bbb96c25b7ab29b1894dcd45e0b3b08fd9d
- https://git.kernel.org/stable/c/ab9337c7cb6f875b6286440b1adfbeeef2b2b2bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48629.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48629
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
