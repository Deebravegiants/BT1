# [H] CVE-2018-7713

## Summary
Severity: High
Advisory: CVE-2018-7713
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2018-7713
Type: osv

## Details
The validateInputImageSize function in modules/imgcodecs/src/loadsave.cpp in OpenCV 3.4.1 allows remote attackers to cause a denial of service (assertion failure) because (size.width <= (1<<20)) may be false. Note: “OpenCV CV_Assert is not an assertion (C-like assert()), it is regular C++ exception which can raised in case of invalid or non-supported parameters.

## References
- https://github.com/xiaoqx/pocs/tree/master/opencv/dos-by-assert
- https://github.com/opencv/opencv/issues/10998
