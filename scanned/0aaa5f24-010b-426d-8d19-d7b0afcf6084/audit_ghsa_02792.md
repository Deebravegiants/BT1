# [H] coreos-installer improperly verifies GPG signature when decompressing gzipped artifact

## Summary
Severity: High
Advisory: GHSA-3r3g-g73x-g593
CVE: CVE-2021-20319
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-3r3g-g73x-g593
Type: github-advisory

## Affected
- crates.io: `coreos-installer` — affected >=0 <0.10.1

## Details
### Impact

coreos-installer fails to correctly verify GPG signatures when decompressing gzip-compressed artifacts.  This allows bypass of signature verification in cases where coreos-installer decompresses a downloaded OS image, allowing an attacker who can modify the OS image to compromise a newly-installed system.

Default installations from ISO or PXE media in Fedora CoreOS, RHEL CoreOS, and RHEL for Edge are **not** affected, as coreos-installer installs from an OS image shipped as part of the install media.

These flows are affected:

1.  Installing with `--image-file`, `--image-url`, or `coreos.inst.image_url`.  For example, if a user has a local mirror of installation images, an attacker could replace an image with a gzip-compressed alternative (even if the file extension is `.xz`).  The result:

    ```
    $ coreos-installer install --image-url http://localhost:8080/image.xz /dev/loop0
    Downloading image from http://localhost:8080/image.xz
    Downloading signature from http://localhost:8080/image.xz.sig
    > Read disk 749.9 MiB/749.9 MiB (100%)
    gpg: Signature made Mon 20 Sep 2021 02:41:50 PM EDT
    gpg: using RSA key 8C5BA6990BDB26E19F2A1A801161AE6945719A39
    gpg: BAD signature from "Fedora (34) <fedora-34-primary@fedoraproject.org>" [ultimate]
    Install complete.
    ```

    Notice that GPG reports a bad signature, but coreos-installer continues anyway.  Automation that relies on coreos-installer's exit status will not notice either.

2. `coreos-installer download --decompress --image-url`:

    ```
    $ coreos-installer download --decompress --image-url http://localhost:8080/image.xz
    > Read disk 749.9 MiB/749.9 MiB (100%)
    gpg: Signature made Mon 20 Sep 2021 02:41:50 PM EDT
    gpg: using RSA key 8C5BA6990BDB26E19F2A1A801161AE6945719A39
    gpg: BAD signature from "Fedora (34) <fedora-34-primary@fedoraproject.org>" [ultimate]
    ./image
    ```

    Again, coreos-installer reports success.

3. Installing with default parameters, when **not** installing from the image built into live ISO or PXE media, if the hosting service is compromised or if an active attacker gains control of the HTTPS response.

4. `coreos-installer download --decompress` if the hosting service is compromised or if an active attacker gains control of the HTTPS response.

### Patches

The vulnerability is [fixed](https://github.com/coreos/coreos-installer/pull/659) in coreos-installer 0.10.1.

### Workarounds

For `coreos-installer download`, do not use the `-d` or `--decompress` options.

For `coreos-installer install`, manually inspect the stderr output.  If `BAD signature` appears, do not boot from the target disk.  Note, however, that some OS services may have already accessed data on the compromised disk.

### References

For more information, see [PR 655](https://github.com/coreos/coreos-installer/pull/655).

### For more information

If you have any questions or comments about this advisory, [open an issue in coreos-installer](https://github.com/coreos/coreos-installer/issues/new/choose) or email the CoreOS [development mailing list](https://lists.fedoraproject.org/archives/list/coreos@lists.fedoraproject.org/).

## References
- https://github.com/coreos/coreos-installer/security/advisories/GHSA-3r3g-g73x-g593
- https://nvd.nist.gov/vuln/detail/CVE-2021-20319
- https://github.com/coreos/coreos-installer/pull/655
- https://github.com/coreos/coreos-installer/pull/659/commits/ad243c6f0eff2835b2da56ca5f7f33af76253c89
- https://bugzilla.redhat.com/show_bug.cgi?id=2011862
- https://github.com/coreos/coreos-installer
- https://rustsec.org/advisories/RUSTSEC-2022-0103.html
