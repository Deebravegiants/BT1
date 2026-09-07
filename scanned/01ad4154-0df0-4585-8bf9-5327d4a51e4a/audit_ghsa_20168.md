# [M] QueryInterface should call AddRef before returning pointer

## Summary
Severity: Medium
Advisory: GHSA-9rg7-3j4f-cf4x
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-9rg7-3j4f-cf4x
Type: github-advisory

## Affected
- crates.io: `derive-com-impl` — affected >=0 <0.1.2

## Details
Affected version of this crate, which is a required dependency in com-impl, 
provides a faulty implementation of the `IUnknown::QueryInterface` method.

`QueryInterface` implementation must call `IUnknown::AddRef` before returning the pointer,
as describe in this documentation:
<https://docs.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-queryinterface(refiid_void)>

As it is not incrementing the refcount as expected, the following calls to `IUnknown::Release` method 
will cause WMI to drop reference to the interface, and can lead to invalid reference.

This is documented in <https://docs.microsoft.com/en-us/windows/win32/learnwin32/managing-the-lifetime-of-an-object#reference-counting>

There is no simple workaround, as you can't know how many time QueryInterface will be called.
The only way to quick fix this is to use the macro expanded version of the code and modify 
the QueryInterface method to add the AddRef call yourself.

The issue was corrected in commit `9803f31fbd1717d482d848f041044d061fca6da7`.

## References
- https://github.com/Connicpu/com-impl/issues/1
- https://github.com/Connicpu/com-impl/commit/9803f31fbd1717d482d848f041044d061fca6da7
- https://github.com/Connicpu/com-impl
- https://rustsec.org/advisories/RUSTSEC-2021-0083.html
