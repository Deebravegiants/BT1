# [M] MLX has Wild Pointer Dereference in load_gguf()

## Summary
Severity: Medium
Advisory: GHSA-j842-xgm4-wf88
CVE: CVE-2025-62609
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-11-21
Source: https://github.com/advisories/GHSA-j842-xgm4-wf88
Type: github-advisory

## Affected
- PyPI: `mlx` — affected >=0 <0.29.4

## Details
## Summary

Segmentation fault in `mlx::core::load_gguf()` when loading malicious GGUF files. Untrusted pointer from external gguflib library is dereferenced without validation, causing application crash.

Environment:
- OS: Ubuntu 20.04.6 LTS
- Compiler: Clang 19.1.7

## Vulnerability

**Location**: `mlx/io/gguf.cpp`
- Function `extract_tensor_data()` at lines 59-79
- Vulnerable memcpy at lines 64-67
- Called from `load_arrays()` at line 177

**The Bug**:
```cpp
std::tuple<allocator::Buffer, Dtype> extract_tensor_data(gguf_tensor* tensor) {
  std::optional<Dtype> equivalent_dtype = gguf_type_to_dtype(tensor->type);
  if (equivalent_dtype.has_value()) {
    allocator::Buffer buffer = allocator::malloc(tensor->bsize);
    memcpy(
        buffer.raw_ptr(),
        tensor->weights_data,  // untrusted pointer from gguflib
        tensor->num_weights * equivalent_dtype.value().size());
    return {buffer, equivalent_dtype.value()};
  }
  // ...
}
```

## Possible Fix

```cpp
std::tuple<allocator::Buffer, Dtype> extract_tensor_data(gguf_tensor* tensor) {
  std::optional<Dtype> equivalent_dtype = gguf_type_to_dtype(tensor->type);
  if (equivalent_dtype.has_value()) {
    // FIX: Validate pointer
    if (!tensor->weights_data) {
      throw std::runtime_error("[load_gguf] NULL tensor data pointer");
    }

    allocator::Buffer buffer = allocator::malloc(tensor->bsize);
    memcpy(
        buffer.raw_ptr(),
        tensor->weights_data,
        tensor->num_weights * equivalent_dtype.value().size());
    return {buffer, equivalent_dtype.value()};
  }
  // ...
}
```

## PoC

```bash
# Install MLX
pip install mlx

python3 -c "import mlx.core as mx; mx.load('exploit.gguf', format='gguf')"
```

Download the poc file [there](https://drive.google.com/file/d/1t9Z2RJGn-oHmluKWebU077UWSMGXeuVp/view?usp=sharing), or let me know how I can send it to you.

**AddressSanitizer Output (with instrumented build)**:
```
AddressSanitizer:DEADLYSIGNAL
=================================================================
==5855==ERROR: AddressSanitizer: SEGV on unknown address 0x7fc432f64bc0 (pc 0x7fc430841c12 bp 0x7ffc04847ab0 sp 0x7ffc04847268 T0)
==5855==The signal is caused by a READ memory access.
    #0 0x7fc430841c12  /build/glibc-B3wQXB/glibc-2.31/string/../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:312
    #1 0x55aac829756b in __asan_memcpy (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x9ef56b) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)
    #2 0x55aacaa6e8dc in mlx::core::extract_tensor_data(gguf_tensor*) /home/user1/mlx/mlx/io/gguf.cpp:64:5
    #3 0x55aacaa773fc in mlx::core::load_arrays[abi:cxx11](gguf_ctx*) /home/user1/mlx/mlx/io/gguf.cpp:226:35
    #4 0x55aacaa782a9 in mlx::core::load_gguf(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char>> const&, std::variant<std::monostate, mlx::core::Stream, mlx::core::Device>) /home/user1/mlx/mlx/io/gguf.cpp:250:17
    #5 0x55aac82dc696 in LLVMFuzzerTestOneInput /home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf.cpp:49:19
    #6 0x55aac81e25c6 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x93a5c6) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)
    #7 0x55aac81cc738 in fuzzer::RunOneTest(fuzzer::Fuzzer*, char const*, unsigned long) (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x924738) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)
    #8 0x55aac81d220a in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x92a20a) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)
    #9 0x55aac81fbb82 in main (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x953b82) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)
    #10 0x7fc4307aa082 in __libc_start_main /build/glibc-B3wQXB/glibc-2.31/csu/../csu/libc-start.c:308:16
    #11 0x55aac81c73ed in _start (/home/user1/mlx/fuzz/load_gguf/fuzz_load_gguf+0x91f3ed) (BuildId: 57467f1ce96052757daeef4b04739be7f23c5f1f)

==5855==Register values:
rax = 0x0000502000000098  rbx = 0xfafafafa0000fa00  rcx = 0x00000a047fff8013  rdx = 0x0000000000000008
rdi = 0x0000502000000098  rsi = 0x00007fc432f64bc0  rbp = 0x00007ffc04847ab0  rsp = 0x00007ffc04847268
 r8 = 0x00000a0400000013   r9 = 0x0000000000000000  r10 = 0x00000a0400000013  r11 = 0x0000000000000000
r12 = 0x00000a047fff8010  r13 = 0xffffffffffffffc7  r14 = 0x00007fc42dd00280  r15 = 0x00000ff885ba0050
AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /build/glibc-B3wQXB/glibc-2.31/string/../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:312
==5855==ABORTING
```

## Impact

- **Attack vector**: Malicious GGUF file (model weights, typically from untrusted sources)
- **Affects**: MLX users on all platforms who call the vulnerable method with unsanitized input.
- **Result**: Segmentation fault (uncatchable by exception handlers)

---
Credits:

- Markiyan Melnyk (ARIMLABS)
- Mykyta Mudryi (ARIMLABS)
- Markiyan Chaklosh (ARIMLABS)

## References
- https://github.com/ml-explore/mlx/security/advisories/GHSA-j842-xgm4-wf88
- https://nvd.nist.gov/vuln/detail/CVE-2025-62609
- https://github.com/ml-explore/mlx
- https://github.com/pypa/advisory-database/tree/main/vulns/mlx/PYSEC-2025-139.yaml
