# [M] Matrix Media Repo (MMR) allows untrusted file formats can be thumbnailed, invoking potentially further untrusted decoders

## Summary
Severity: Medium
Advisory: GHSA-rcxc-wjgw-579r
CVE: CVE-2024-56515
CWE: CWE-434, CWE-502
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-16
Source: https://github.com/advisories/GHSA-rcxc-wjgw-579r
Type: github-advisory

## Affected
- Go: `github.com/t2bot/matrix-media-repo` — affected >=0 <1.3.8

## Details
### Impact

If SVG or JPEGXL thumbnailers are enabled (they are disabled by default), a user may upload a file which claims to be either of these types and request a thumbnail to invoke a different decoder in ImageMagick. In some ImageMagick installations, this includes the capability to run Ghostscript to decode the image/file.

If MP4 thumbnailers are enabled (also disabled by default), the same issue as above may occur with the ffmpeg installation instead.

MMR uses a number of other decoders for all other file types when preparing thumbnails. Theoretical issues are possible with these decoders, however in testing they were not possible to exploit.

### Patches

This is fixed in [MMR v1.3.8](https://github.com/t2bot/matrix-media-repo/releases/tag/v1.3.8). MMR now inspects the mimetype of media prior to thumbnailing, and picks a thumbnailer based on those results instead of relying on user-supplied values. This may lead to fewer thumbnails when obscure file shapes are used. This also helps narrow scope of theoretical issues with all decoders MMR uses for thumbnails.

### Workarounds

Disabling the SVG, JPEGXL, and MP4 thumbnail types in the MMR config prevents the decoders from being invoked. Further disabling uncommon file types on the server is recommended to limit risk surface. 

Containers and other similar technologies may also be used to limit the impact of vulnerabilities in external decoders, like ImageMagick and ffmpeg. 

Some installations of ImageMagick may disable "unsafe" file types, like PDFs, already. This option can be replicated to other environments as needed. ffmpeg may be compiled with limited decoders/codecs. The Docker image for MMR disables PDFs and similar formats by default.

### References

A similar issue was discovered in Synapse: https://github.com/element-hq/synapse/security/advisories/GHSA-vp6v-whfm-rv3g

## References
- https://github.com/t2bot/matrix-media-repo/security/advisories/GHSA-rcxc-wjgw-579r
- https://nvd.nist.gov/vuln/detail/CVE-2024-56515
- https://github.com/t2bot/matrix-media-repo
- https://github.com/t2bot/matrix-media-repo/releases/tag/v1.3.8
- https://pkg.go.dev/vuln/GO-2025-3400
