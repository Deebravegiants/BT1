# [M] OpenEXR Out-Of-Memory via Unbounded File Header Values

## Summary
Severity: Medium
Advisory: GHSA-x22w-82jp-8rvf
CVE: CVE-2025-48074
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-x22w-82jp-8rvf
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.3.2 <3.3.3

## Details
### Summary
The OpenEXR file format defines many information about the final image inside of the file header, such as the size of data/display window.

The application trusts the value of `dataWindow` size provided in the header of the input file, and performs computations based on this value.

This may result in unintended behaviors, such as excessively large number of iterations and/or huge memory allocations.


### Details
A concrete example of this issue is present in the function `readScanline()` in `ImfCheckFile.cpp` at line 235, that performs a for-loop using the `dataWindow min.y` and `max.y` coordinates that can be arbitrarily large.

```cpp
in.setFrameBuffer (i);

int step = 1;

//
// try reading scanlines. Continue reading scanlines
// even if an exception is encountered
//
for (int y = dw.min.y; y <= dw.max.y; y += step) // <-- THIS LOOP IS EXCESSIVE BECAUSE OF DW.MAX
{
    try
    {
        in.readPixels (y);
    }
    catch (...)
    {
        threw = true;

        //
        // in reduceTime mode, fail immediately - the file is corrupt
        //
        if (reduceTime) { return threw; }
    }
}
```

Another example occurs in the `EnvmapImage::resize` function that in turn calls `Array2D<T>::resizeEraseUnsafe` passing the `dataWindow` X and Y coordinates and perform a huge allocation.

On some system, the allocator will simply return `std::bad_alloc` and crash. On other systems such as macOS, the allocator will happily continue with a "small" pre-allocation and allocate further memory whenever it is accessed.
This is the case with the `EnvmapImage::clear` function that is called right after and fills the image RGB values with zeros, allocating tens of Gigabytes.

### PoC

NOTE: please download the `oom_crash.exr` file via the following link:
 
https://github.com/ShielderSec/poc/tree/main/CVE-2025-48074

1. Compile the `exrcheck` binary in a macOS or GNU/Linux machine with ASAN.
2. Open the `oom_crash.exr` file with the following command:

```
exrcheck oom_crash.exr
```

3. Notice that `exrenvmap`/`exrcheck` crashes with ASAN stack-trace.

### Impact
An attacker could cause a denial of service by stalling the application or exhaust memory by stalling the application in a loop which contains a memory leakage.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-x22w-82jp-8rvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-48074
- https://github.com/AcademySoftwareFoundation/openexr/commit/2df7802a6421bf39ed73a607392f01b3c6da4e4a
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/ShielderSec/poc/tree/main/CVE-2025-48074
