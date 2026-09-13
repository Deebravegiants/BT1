# [M] Partial path traversal in sharpcompress

## Summary
Severity: Medium
Advisory: GHSA-jp7f-grcv-6mjf
CVE: CVE-2021-39208
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-jp7f-grcv-6mjf
Type: github-advisory

## Affected
- NuGet: `SharpCompress` — affected >=0 <0.29

## Details
SharpCompress recreates a hierarchy of directories under destinationDirectory if ExtractFullPath is set to true in options. In order to prevent extraction outside the destination directory the destinationFileName path is verified to begin with fullDestinationDirectoryPath. However it is not enforced that fullDestinationDirectoryPath ends with slash:

```csharp
public static void WriteEntryToDirectory(IEntry entry,
                                         string destinationDirectory,
                                         ExtractionOptions? options,
                                         Action<string, ExtractionOptions?> write)
{
    string destinationFileName;
    string file = Path.GetFileName(entry.Key);
    string fullDestinationDirectoryPath = Path.GetFullPath(destinationDirectory);
...
        throw new ExtractionException("Entry is trying to write a file outside of the destination directory.");
}
```

If the destinationDirectory is not slash terminated like /home/user/dir it is possible to create a file with a name thats begins as the destination directory one level up from the directory, i.e. /home/user/dir.sh.

#### Impact
Because of the file name and destination directory constraints the arbitrary file creation impact is limited and depends on the use case.

## References
- https://github.com/adamhathcock/sharpcompress/security/advisories/GHSA-jp7f-grcv-6mjf
- https://nvd.nist.gov/vuln/detail/CVE-2021-39208
- https://github.com/adamhathcock/sharpcompress/pull/614
- https://github.com/adamhathcock/sharpcompress/commit/ea5c8dc06314c7a5068e7901c51a625224d2b288
- https://github.com/adamhathcock/sharpcompress
- https://github.com/adamhathcock/sharpcompress/releases/tag/0.29.0
