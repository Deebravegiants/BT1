# [H] motionEye's Absolute Path Traversal in Media File Handlers Allows Arbitrary File Read

## Summary
Severity: High
Advisory: GHSA-rw9q-97r9-8gvh
CVE: CVE-2026-55488
CWE: CWE-22
Ecosystem: PyPI
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-rw9q-97r9-8gvh
Type: github-advisory

## Affected
- PyPI: `motioneye` — affected >=0 <0.44.0

## Details
### Summary

mEye contains an absolute path traversal vulnerability in multiple media file handlers that allows an attacker to read arbitrary files from the filesystem.

The affected handlers accept a user-controlled filename parameter and construct filesystem paths using `os.path.join()`. When an absolute path is supplied, Python discards the configured media directory and returns the attacker-supplied path directly. The application then bypasses Tornado's built-in path validation by overriding the relevant safety checks.

As a result, an attacker can access files outside of the configured camera media directory, subject to the permissions of the motionEye process.

### Details

The issue exists in the media playback and download functionality.

The filename parameter is passed to `mediafiles.get_media_path()`:

```python
def get_media_path(camera_config, path, media_type):
    target_dir = camera_config.get('target_dir')
    full_path = os.path.join(target_dir, path)
    return full_path
```

When path is an absolute path (e.g. `/etc/motioneye/motion.conf`), Python's `os.path.join()` discards `target_dir` entirely and returns the absolute path as-is. This would normally be caught by Tornado's StaticFileHandler path validation, but MoviePlaybackHandler explicitly overrides both safety checks (`movie_playback.py` lines 111-115):

```
def get_absolute_path(self, root, path):
    return path

def validate_absolute_path(self, root, absolute_path):
    return absolute_path
```
This allows reading any file on the filesystem that the motionEye process can access.

The same path traversal exists in the movie download, picture download, and picture preview handlers:

- GET /movie/<camera_id>/download/<filename>
- GET /picture/<camera_id>/download/<filename>
- GET /picture/<camera_id>/preview/<filename>

# PoC

```
GET /movie/1/playback//etc/motioneye/motion.conf HTTP/1.1
Host: target:8765
```

# Fix

Do not allow absolute paths supplied by user input.

Validate that the fully resolved canonical path remains within the configured camera media directory before serving a file.

Additionally, Tornado’s built-in path validation should not be bypassed unless equivalent validation is performed by motionEye.

## References
- https://github.com/motioneye-project/motioneye/security/advisories/GHSA-rw9q-97r9-8gvh
- https://github.com/motioneye-project/motioneye
