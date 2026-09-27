# [M] Starlette has possible denial-of-service vector when parsing large files in multipart forms

## Summary
Severity: Medium
Advisory: GHSA-2c2j-9gv5-cj73
CVE: CVE-2025-54121
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-07-21
Source: https://github.com/advisories/GHSA-2c2j-9gv5-cj73
Type: github-advisory

## Affected
- PyPI: `starlette` — affected >=0 <0.47.2

## Details
### Summary
When parsing a multi-part form with large files (greater than the [default max spool size](https://github.com/encode/starlette/blob/fa5355442753f794965ae1af0f87f9fec1b9a3de/starlette/formparsers.py#L126)) `starlette` will block the main thread to roll the file over to disk. This blocks the event thread which means we can't accept new connections.

### Details
Please see this discussion for details: https://github.com/encode/starlette/discussions/2927#discussioncomment-13721403. In summary the following UploadFile code (copied from [here](https://github.com/encode/starlette/blob/fa5355442753f794965ae1af0f87f9fec1b9a3de/starlette/datastructures.py#L436C5-L447C14)) has a minor bug. Instead of just checking for `self._in_memory` we should also check if the additional bytes will cause a rollover.

```python

    @property
    def _in_memory(self) -> bool:
        # check for SpooledTemporaryFile._rolled
        rolled_to_disk = getattr(self.file, "_rolled", True)
        return not rolled_to_disk

    async def write(self, data: bytes) -> None:
        if self.size is not None:
            self.size += len(data)

        if self._in_memory:
            self.file.write(data)
        else:
            await run_in_threadpool(self.file.write, data)
```

I have already created a PR which fixes the problem: https://github.com/encode/starlette/pull/2962


### PoC
See the discussion [here](https://github.com/encode/starlette/discussions/2927#discussioncomment-13721403) for steps on how to reproduce.

### Impact
To be honest, very low and not many users will be impacted. Parsing large forms is already CPU intensive so the additional IO block doesn't slow down `starlette` that much on systems with modern HDDs/SSDs. If someone is running on tape they might see a greater impact.

## References
- https://github.com/encode/starlette/security/advisories/GHSA-2c2j-9gv5-cj73
- https://nvd.nist.gov/vuln/detail/CVE-2025-54121
- https://github.com/encode/starlette/commit/9f7ec2eb512fcc3fe90b43cb9dd9e1d08696bec1
- https://github.com/encode/starlette
- https://github.com/encode/starlette/blob/fa5355442753f794965ae1af0f87f9fec1b9a3de/starlette/datastructures.py#L436C5-L447C14
- https://github.com/encode/starlette/discussions/2927#discussioncomment-13721403
