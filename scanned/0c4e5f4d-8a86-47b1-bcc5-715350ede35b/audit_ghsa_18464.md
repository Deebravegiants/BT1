# [M] OpenEXR ScanLineProcess::run_fill NULL Pointer Write In "reduceMemory" Mode

## Summary
Severity: Medium
Advisory: GHSA-qhpm-86v7-phmm
CVE: CVE-2025-48073
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-qhpm-86v7-phmm
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.3.2 <3.3.3

## Details
### Summary

When reading a deep scanline image with a large sample count in `reduceMemory` mode, it is possible to crash a target application with a NULL pointer dereference in a write operation.

### Details

In the `ScanLineProcess::run_fill` function, implemented in `src/lib/OpenEXR/ImfDeepScanLineInputFile.cpp`, the following code is used to write the `fillValue` in the sample buffer:

```cpp
                switch (fills.type)
                {
                    case OPENEXR_IMF_INTERNAL_NAMESPACE::UINT:
                    {
                        unsigned int fillVal = (unsigned int) (fills.fillValue);
                        unsigned int* fillptr = static_cast<unsigned int*> (dest);

                        for ( int32_t s = 0; s < samps; ++s )
                            fillptr[s] = fillVal; // <--- POTENTIAL CRASH HERE
                        break;
                    }
```

However, when `reduceMemory` mode is enabled in the `readDeepScanLine` function in `src/lib/OpenEXRUtil/ImfCheckFile.cpp`, with large sample counts, the sample data will not be read, as shown below:

```cpp
            // limit total number of samples read in reduceMemory mode
            //
            if (!reduceMemory ||
                fileBufferSize + bufferSize < gMaxBytesPerDeepScanline) // <--- CHECK ON LARGE SAMPLE COUNTS AND reduceMemory
            {
            // SNIP...
            try
                {
                    in.readPixels (y);
                }
```

Therefore, in those cases, the sample buffer would not be allocated, resulting in a potential write operation on a NULL pointer.

### PoC

NOTE: please download the `runfill_crash.exr` file from the following link:
 
https://github.com/ShielderSec/poc/tree/main/CVE-2025-48073

1. Compile the `exrcheck` binary in a macOS or GNU/Linux machine with ASAN.
2. Open the `runfill_crash.exr` file with the following command:

```
exrcheck -m runfill_crash.exr
```

3. Notice that `exrcheck` crashes with ASAN stack-trace.

### Impact
An attacker may cause a denial of service by crashing the application.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-qhpm-86v7-phmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-48073
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/ShielderSec/poc/tree/main/CVE-2025-48073
