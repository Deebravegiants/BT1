# [M] github.com/ulikunitz/xz leaks memory when decoding a corrupted multiple LZMA archives

## Summary
Severity: Medium
Advisory: GHSA-jc7w-c686-c4v9
CVE: CVE-2025-58058
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-jc7w-c686-c4v9
Type: github-advisory

## Affected
- Go: `github.com/ulikunitz/xz` — affected >=0 <0.5.15

## Details
### Summary

It is possible to put data in front of an LZMA-encoded byte stream without detecting the situation while reading the header. This can lead to increased memory consumption because the current implementation allocates the full decoding buffer directly after reading the header. The LZMA header doesn't include a magic number or has  a checksum to detect such an issue according to the [specification](https://github.com/jljusten/LZMA-SDK/blob/master/DOC/lzma-specification.txt).

Note that the code recognizes the issue later while reading the stream, but at this time the memory allocation has already been done.

### Mitigations

The release v0.5.15 includes following mitigations:

- The ReaderConfig DictCap field is now interpreted as a limit for the dictionary size.
- The default is 2 Gigabytes - 1 byte (2^31-1 bytes).
- Users can check with the [Reader.Header] method what the actual values are in  their LZMA files and set a smaller limit using ReaderConfig.
- The dictionary size will not exceed the larger of the file size and the minimum dictionary size. This is another measure to prevent huge memory allocations for the dictionary.
- The code supports stream sizes only up to a pebibyte (1024^5).

Note that the original v0.5.14 version had a compiler error for 32 bit platforms, which has been fixed by v0.5.15.

### Methods affected

Only software that uses [lzma.NewReader](https://pkg.go.dev/github.com/ulikunitz/xz/lzma#NewReader) or [lzma.ReaderConfig.NewReader](https://pkg.go.dev/github.com/ulikunitz/xz/lzma#ReaderConfig.NewReader) is affected. There is no issue for software using the xz functionality.

I thank  @GregoryBuligin for his report, which is provided below.

### Summary
When unpacking a large number of LZMA archives, even in a single goroutine, if the first byte of the archive file is 0 (a zero byte added to the beginning), an error __writeMatch: distance out of range__ occurs. Memory consumption spikes sharply, and the GC clearly cannot handle this situation.

### Details
Judging by the error  __writeMatch: distance out of range__, the problems occur in the code around this function.
https://github.com/ulikunitz/xz/blob/c8314b8f21e9c5e25b52da07544cac14db277e89/lzma/decoderdict.go#L81

### PoC
Run a function similar to this one in 1 or several goroutines on a multitude of LZMA archives that have a 0 (a zero byte) added to the beginning.
```
const ProjectLocalPath = "some/path"
const TmpDir = "tmp"

func UnpackLZMA(lzmaFile string) error {
	file, err := os.Open(lzmaFile)
	if err != nil {
		return err
	}
	defer file.Close()

	reader, err := lzma.NewReader(bufio.NewReader(file))
	if err != nil {
		return err
	}

	tmpFile, err := os.CreateTemp(TmpDir, TmpLZMAPrefix)
	if err != nil {
		return err
	}
	defer func() {
		tmpFile.Close()
		_ = os.Remove(tmpFile.Name())
	}()

	sha256Hasher := sha256.New()
	multiWriter := io.MultiWriter(tmpFile, sha256Hasher)

	if _, err = io.Copy(multiWriter, reader); err != nil {
		return err
	}

	unpackHash := hex.EncodeToString(sha256Hasher.Sum(nil))
	unpackDir := filepath.Join(
		ProjectLocalPath, unpackHash[:2],
	)
	_ = os.MkdirAll(unpackDir, DirPerm)

	unpackPath := filepath.Join(unpackDir, unpackHash)

	return os.Rename(tmpFile.Name(), unpackPath)
}
```



### Impact
Servers with a small amount of RAM that download and unpack a large number of unverified LZMA archives

## References
- https://github.com/ulikunitz/xz/security/advisories/GHSA-jc7w-c686-c4v9
- https://nvd.nist.gov/vuln/detail/CVE-2025-58058
- https://github.com/ulikunitz/xz/commit/88ddf1d0d98d688db65de034f48960b2760d2ae2
- https://github.com/ulikunitz/xz
