# [H] Imageflow affected by libwebp zero-day and should not be used with malicious source images.

## Summary
Severity: High
Advisory: GHSA-7vpr-3ppw-qrpj
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-7vpr-3ppw-qrpj
Type: github-advisory

## Affected
- NuGet: `Imageflow.AllPlatforms` — affected >=0 <0.10.2
- NuGet: `Imageflow.NativeRuntime.win-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeRuntime.osx-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeRuntime.win-x86` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeRuntime.ubuntu-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeRuntime.ubuntu-x86_64-haswell` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeTool.win-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeTool.osx-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeTool.win-x86` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeTool.ubuntu-x86_64` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeTool.ubuntu-x86_64-haswell` — affected >=0 <2.0.0-preview6
- NuGet: `Imageflow.NativeRuntime.ubuntu_18_04-x86_64-haswell` — affected >=0
- NuGet: `Imageflow.NativeRuntime.ubuntu_18_04-x86_64` — affected >=0
- NuGet: `Imageflow.NativeRuntime.osx_10_11-x86_64` — affected >=0
- NuGet: `Imageflow.NativeRuntime.ubuntu_16_04-x86_64` — affected >=0
- NuGet: `Imageflow.NativeTool.ubuntu_18_04-x86_64-haswell` — affected >=0
- NuGet: `Imageflow.NativeTool.ubuntu_16_04-x86_64` — affected >=0
- NuGet: `Imageflow.NativeTool.ubuntu_18_04-x86_64` — affected >=0
- NuGet: `Imageflow.NativeTool.osx_10_11-x86_64` — affected >=0
- NuGet: `Imageflow.Server` — affected >=0 <0.8.2
- NuGet: `ImageResizer.Plugins.Imageflow` — affected >=0 <5.0.12

## Details
### Impact

This vulnerability affects deployments of Imageflow that involve decoding or processing malicious source .webp files. If you only process your own trusted files, this should not affect you (but you should update anyway). 

Imageflow relies on Google's [libwebp] library to decode .webp images, and is affected by the recent zero-day out-of-bounds write vulnerability [CVE-2023-4863](https://nvd.nist.gov/vuln/detail/CVE-2023-4863) and https://github.com/advisories/GHSA-j7hp-h8jx-5ppr. The libwebp vulnerability also affects Chrome, Android, macOS, and other consumers of the library).

libwebp patched [the vulnerability](https://github.com/webmproject/libwebp/commit/2af26267cdfcb63a88e5c74a85927a12d6ca1d76 ) and released [1.3.2](https://github.com/webmproject/libwebp/releases/tag/v1.3.2) 

This was patched in [libwebp-sys in 0.9.3 and 0.9.4](https://github.com/NoXF/libwebp-sys/commits/master)

**[Imageflow v2.0.0-preview8](https://github.com/imazen/imageflow/releases/tag/v2.0.0-preview8) uses the patched version of libwebp as well as updated versions of all dependencies.**

Note: preview 8 requires libc 2.31 or higher on linux and macOS 11 or higher. These restrictions are due to the oldest supported versions of those platforms (which is reflected on Github Actions).

### Patches

**Imageflow v2.0.0-preview8 use the patched version (v1.3.2) of libwebp and libwebp-sys 0.9.4.**
**Imageflow.AllPlatforms 0.10.2 is patched**
**Imageflow.Server v0.8.2 is patched**
**ImageResizer.Plugins.Imageflow 5.0.12 is patched**

### Workarounds

Disable webp decoding using `EnabledCodecs::disable_decoder(NamedDecoders::WebPDecoder)` if using the Rust API. 

Only files that meet the following criteria will be passed to libwebp: 

```rust
bytes.starts_with(b"RIFF") && bytes[8..12].starts_with(b"WEBP")
```

You can utilize matching logic to block webp inputs in your language of choice.

### References

https://github.com/advisories/GHSA-j7hp-h8jx-5ppr
https://nvd.nist.gov/vuln/detail/CVE-2023-4863
https://github.com/webmproject/libwebp/commit/2af26267cdfcb63a88e5c74a85927a12d6ca1d76 
https://github.com/NoXF/libwebp-sys/commits/master

## References
- https://github.com/imazen/imageflow/security/advisories/GHSA-7vpr-3ppw-qrpj
- https://github.com/imazen/imageflow/commit/24894940403a8491fd6495759b8f996ea2da8ad8
- https://github.com/imazen/imageflow
