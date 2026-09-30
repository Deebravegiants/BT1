# [H] ORAS Java: Path traversal in pullArtifact via attacker-controlled org.opencontainers.image.title annotation

## Summary
Severity: High
Advisory: GHSA-xm96-gfjx-jcrc
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-xm96-gfjx-jcrc
Type: github-advisory

## Affected
- Maven: `land.oras:oras-java-sdk` — affected >=0 <0.6.2

## Details
### Summary

The `pullArtifact` methods in `Registry` and `OCILayout` use the `org.opencontainers.image.title` annotation from a pulled manifest as a filename, resolving it against the caller supplied output directory without normalization or a containment check. A manifest publisher can set this annotation to a path that escapes the output directory, causing the SDK to write the layer's blob anywhere the JVM process can write.

### Details

Two call sites are affected.

`src/main/java/land/oras/Registry.java`, `pullLayer` (reached from `Registry.pullArtifact`):

```java
Path targetPath = path.resolve(layer.getAnnotations().get(Const.ANNOTATION_TITLE));
...
Files.copy(is, targetPath, StandardCopyOption.REPLACE_EXISTING);
```

`src/main/java/land/oras/OCILayout.java`, `OCILayout.pullArtifact`:

```java
Files.copy(blobPath, path.resolve(layer.getAnnotations().get(Const.ANNOTATION_TITLE)));
```

The annotation comes from the remote manifest. `Path.resolve` treats an absolute argument as a full override of the base, and follows `..` segments upward, so the annotation controls the destination. `REPLACE_EXISTING` overwrites files that exist at that destination.

The unpack branch of `pullLayer` (taken when the layer carries `io.deis.oras.content.unpack=true`) is not affected, because it dispatches through `ArchiveUtils.untar` / `unzip`, which apply `outputPath.startsWith(normalizedTarget)` after normalization. The non unpack branch and `OCILayout.pullArtifact` lack the equivalent check.

`fetchBlob(ContainerRef, Path)` is not affected. The caller passes the destination path and the title annotation is not consulted.

## References
- https://github.com/oras-project/oras-java/security/advisories/GHSA-xm96-gfjx-jcrc
- https://github.com/oras-project/oras-java
