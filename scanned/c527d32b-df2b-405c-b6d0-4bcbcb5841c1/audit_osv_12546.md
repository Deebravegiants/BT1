# [C] CVE-2018-12713

## Summary
Severity: Critical
Advisory: CVE-2018-12713
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-06-24
Source: https://osv.dev/vulnerability/CVE-2018-12713
Type: osv

## Details
GIMP through 2.10.2 makes g_get_tmp_dir calls to establish temporary filenames, which may result in a filename that already exists, as demonstrated by the gimp_write_and_read_file function in app/tests/test-xcf.c. This might be leveraged by attackers to overwrite files or read file content that was intended to be private.

## References
- https://gitlab.gnome.org/GNOME/gimp/issues/1689
- https://github.com/GNOME/gimp/commit/c21eff4b031acb04fb4dfce8bd5fdfecc2b6524f
