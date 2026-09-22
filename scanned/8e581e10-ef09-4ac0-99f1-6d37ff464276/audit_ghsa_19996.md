# [H] Path Traversal In MeterSpere leads to upload file to any path

## Summary
Severity: High
Advisory: GHSA-9p62-x3c5-hr5p
CVE: CVE-2022-46178
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-9p62-x3c5-hr5p
Type: github-advisory

## Affected
- Maven: `io.metersphere:metersphere` — affected >=0 <2.5.1

## Details
### Summary

MeterSphere allow users to upload file, but not check the file name, may lead to upload file to any path if the file name in upload request is falsified.

### Details

Metersphere's [`FileUtils.java`](https://github.com/metersphere/metersphere/blob/v2.5.0/framework/sdk-parent/sdk/src/main/java/io/metersphere/commons/utils/FileUtils.java#L57) didn't check the filePath.

```java
    public static void createFile(String filePath, byte[] fileBytes) {
        File file = new File(filePath);
        if (file.exists()) {
            file.delete();
        }
        try {
            File dir = file.getParentFile();
            if (!dir.exists()) {
                dir.mkdirs();
            }
            file.createNewFile();
        } catch (Exception e) {
            LogUtil.error(e);
        }

        try (InputStream in = new ByteArrayInputStream(fileBytes); OutputStream out = new FileOutputStream(file)) {
            final int MAX = 4096;
            byte[] buf = new byte[MAX];
            for (int bytesRead = in.read(buf, 0, MAX); bytesRead != -1; bytesRead = in.read(buf, 0, MAX)) {
                out.write(buf, 0, bytesRead);
            }
        } catch (IOException e) {
            LogUtil.error(e);
            MSException.throwException(Translator.get("upload_fail"));
        }
    }
```

### Patches

The vulnerability has been fixed in [v2.5.1](https://github.com/metersphere/metersphere/releases/tag/v2.5.1).

https://github.com/metersphere/metersphere/commit/3a890eeeb8a6b0887927c876a73bdb3a99a82138 : add validation for file name.

### Workarounds

It is recommended to upgrade the version to [v2.5.1](https://github.com/metersphere/metersphere/releases/tag/v2.5.1).

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/metersphere/metersphere/issues).

## References
- https://github.com/metersphere/metersphere/security/advisories/GHSA-9p62-x3c5-hr5p
- https://nvd.nist.gov/vuln/detail/CVE-2022-46178
- https://github.com/metersphere/metersphere
- https://github.com/metersphere/metersphere/blob/v2.5.0/framework/sdk-parent/sdk/src/main/java/io/metersphere/commons/utils/FileUtils.java#L5
- https://github.com/metersphere/metersphere/releases/tag/v2.5.1
