# [C] CVE-2020-11105

## Summary
Severity: Critical
Advisory: CVE-2020-11105
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-30
Source: https://osv.dev/vulnerability/CVE-2020-11105
Type: osv

## Details
An issue was discovered in USC iLab cereal through 1.3.0. It employs caching of std::shared_ptr values, using the raw pointer address as a unique identifier. This becomes problematic if an std::shared_ptr variable goes out of scope and is freed, and a new std::shared_ptr is allocated at the same address. Serialization fidelity thereby becomes dependent upon memory layout. In short, serialized std::shared_ptr variables cannot always be expected to serialize back into their original values. This can have any number of consequences, depending on the context within which this manifests.

## References
- https://github.com/USCiLab/cereal/issues/636
