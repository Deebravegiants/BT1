# [H] Flooding Server with Thumbnail files

## Summary
Severity: High
Advisory: GHSA-277c-5vvj-9pwx
CVE: CVE-2024-32871
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-277c-5vvj-9pwx
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=11.0.0 <11.2.4

## Details
# Details
## 1. All Imagick supported Fileformats are served without filtering

The Thumbnail endpoint does not check against any filters what file formats should be served. We can transcode the image in all formats imagemagick supports. With that we can create Files that are much larger in filesize than the original. For example we can create a .txt file for all thumbnails, and we get the text representation of the image.

We can demonstrate that with the pimcore demo: 

This Thumbnail is found on the Frontend: https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89.avif (12kb Filesize)

We can generate a text representation by simply changing the file extension: https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89.txt (4.59mb Filesize)

Other (large) fileformats we tested: ftxt, dip, bmp, bmp3, bmp2, farbfeld, cmyk, cmyka, ycbcr, ycbcra and many more (just check imagemagick supported formats)

With that we can fill the available space of a server really easy.

With formats like yaml or json we can also expose exif data of the original image file - could be a concern with gps data in user uploaded images.

### TLDR

- we can generate all imagemagick supported formats with all thumbnail configs
- all configs were the format is set to "auto (Web-optimized)" are vulnerable
- private (exif) data can be exposed.
- We can flood the the server with a bunch of files that are a multiple magnitudes of the original thumbnail size (see txt example), for all thumbnail configs, with every image that we find (scriptable)

### Proposed Solution

Implement a list of allowed formats that the developer can modify if needed, if a file is requested in another format than listed, pimcore should return either "/bundles/pimcoreadmin/img/filetype-not-supported.svg" or a 404.

```yaml
pimcore:
    thumbnails:
    	allowed_formats: ['jpg', 'png', 'avif', 'webp', 'gif']
```

For non-maintained Pimcore versions (<11), the webserver config could be used to only serve files that should be allowed. 

## 2. Non Web optimized file formats (ORIGINAL, JPG, PNG)  creates duplicated files on Server

With Thumbnail config that are configured to serve non web optimized file formats (such as ORIGINAL, jpg, png, print, etc) we can create files with arbitrary file formats that are saved to disk.

For example, the thumbnail configuration "print_backgroundimage" (in the pimcore demo) can be used to create files such as: 

https://demo.pimcore.fun/Car%20Images/jaguar/3/image-thumb__3__print_backgroundimage/auto-3095119.aaa
https://demo.pimcore.fun/Car%20Images/jaguar/3/image-thumb__3__print_backgroundimage/auto-3095119.aab
https://demo.pimcore.fun/Car%20Images/jaguar/3/image-thumb__3__print_backgroundimage/auto-3095119.aac 

Each request creates a new copy of the original (jpg) thumbnail file. The server can be flooded with a bunch of files.

Code for this mechanism is here: https://github.com/pimcore/pimcore/blob/11.x/models/Asset/Service.php#L621-L623

### Proposed Solution

Use same filtered list from "All Imagick supported Fileformats are served without filtering" and do not copy the arbitrary file to disk, just serve the original image file under the "new" name.

## 3. Scaling Factor is not limited and can be modified via url

We can scale each thumbnail to an arbitrary factor with @<float>x added to the request url.

For example: 

https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@1x.avif
https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@1.01x.avif
https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@1.08x.avif
https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@2x.avif

If the thumbnail config allows "forced" resizing, we could also do something like:

https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@192x.avif  

Each request will create a new file, flooding the server with more files.
If the factor is big enough, we can also max out the CPU with a single request for quite some time (only really a problem with "forced")

In combination with the first vulnerability we can also generate (large) text files for scaled images:

https://demo.pimcore.fun/Sample%20Content/Background%20Images/317/image-thumb__317__standardTeaser/11.8c64bd89@4x.txt (6.6 mb filesize)

### Proposed solution

Limit scale factors with an allowlist:

```yaml
pimcore:
    thumbnails:
    	allowed_scale_factors: [1.25, 1.5, 2, 4]
```


# Impact
All Pimcore Instances are affected, as far as we can see, also all versions

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-277c-5vvj-9pwx
- https://nvd.nist.gov/vuln/detail/CVE-2024-32871
- https://github.com/pimcore/pimcore/commit/38af70b3130f16fc27f2aea34e2943d7bdaaba06
- https://github.com/pimcore/pimcore/commit/a6821a16ea38086bf6012e682e1743488244bd85
- https://github.com/pimcore/pimcore
