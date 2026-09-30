# [H] exiftool-vendored vulnerable to argument injection via newline characters in tag names

## Summary
Severity: High
Advisory: GHSA-cw26-7653-2rp5
CVE: CVE-2026-43893
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-cw26-7653-2rp5
Type: github-advisory

## Affected
- npm: `exiftool-vendored` — affected >=0 <35.19.0

## Details
### Impact

`exiftool-vendored` starts ExifTool in `-stay_open True -@ -` mode, where arguments are read from stdin one per line. In affected versions, several caller-supplied strings were interpolated into ExifTool arguments without rejecting line delimiters. A newline or carriage return inside one of those strings could split a single intended argument into multiple ExifTool arguments, allowing argument injection. The fix also rejects NUL bytes as unsafe control characters.

Applications that pass attacker-controlled strings to affected APIs may allow an attacker to make ExifTool read files accessible to the ExifTool process, or write output to attacker-chosen file system paths accessible to that process. No remote code execution has been demonstrated.

The reported write-path issue is caused by unsanitized tag **keys**. Tag **values** passed to `ExifTool#write` are not affected, because `WriteTask` already encodes whitespace characters in values (e.g. `\n` -> `&#10;`) before transmission.

Confirmed affected inputs:

- **Tag-name arguments / tag keys** — keys of the `tags` object passed to `ExifTool#write`; entries of the `retain` option to `ExifTool#deleteAllTags`; entries of the `numericTags` option to `ExifTool#read`; the `tagname` argument to `ExifTool#extractBinaryTag` and `#extractBinaryTagToBuffer`.
- **Filename / path arguments** to `ExifTool#write`, `#read`, `#readRaw`, `#deleteAllTags`, `#rewriteAllTags`, `#extractBinaryTag`, `#extractBinaryTagToBuffer`, and the binary-extraction convenience methods `#extractJpgFromRaw`, `#extractPreview`, and `#extractThumbnail`. `path.resolve()` does not strip newlines, so an application that accepts attacker-controlled filenames containing newline characters was vulnerable.
- **The `imageHashType` option** to `ExifTool#read`. TypeScript types restrict this to a literal union, but JS callers or callers with weakened type checking could reach the sink.

Applications that only pass hardcoded strings for tag names, options, and filenames are not affected.

### Patches

Fixed in **v35.19.0**. Two layers of defense:

1. **Per-site input validation.** A new `validateTagName` helper rejects any tag-name string containing characters outside the ExifTool tag grammar (letters, digits, `:`, `-`, `_`, and the ExifTool modifiers `*`, `?`, `+`, `#`). Applied at every tag-name interpolation site.
2. **Defense-in-depth at the command renderer.** `ExifToolTask.renderCommand` now rejects _any_ argument containing `\r`, `\n`, or `\0` before it is sent to the ExifTool process. This catches injection via filename arguments, option values, and any future interpolation site that forgets the per-site validator.

### Workarounds

Upgrade to v35.19.0 or later.

If upgrading immediately is not possible, reject untrusted strings containing control characters before passing them to the affected APIs. Conservative guard:

```ts
function assertSafeForExifTool(s: string): void {
  if (typeof s !== "string" || /[\x00-\x20=<>]/.test(s)) {
    throw new Error("Rejected unsafe string for ExifTool");
  }
}
```

Apply to tag names, `retain` / `numericTags` entries, binary-extraction tag names, filenames, and the `imageHashType` option. This is a denylist and is strictly weaker than the library's internal validator; it is sufficient to block the known PoCs but will accept strings that the library itself now rejects.

### Resources

- ExifTool `-stay_open` / argument-file documentation: https://exiftool.org/exiftool_pod.html#stay_open-FLAG
- ExifTool tag-name reference: https://exiftool.org/TagNames/
- CWE-88: Improper Neutralization of Argument Delimiters in a Command ('Argument Injection') — https://cwe.mitre.org/data/definitions/88.html

### Credit

- Reporter: Hank Tam
- Affiliation: Independent

## References
- https://github.com/photostructure/exiftool-vendored.js/security/advisories/GHSA-cw26-7653-2rp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43893
- https://exiftool.org/TagNames
- https://exiftool.org/exiftool_pod.html#stay_open-FLAG
- https://github.com/photostructure/exiftool-vendored.js
