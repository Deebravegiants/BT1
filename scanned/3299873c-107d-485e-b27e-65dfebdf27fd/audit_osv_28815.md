# [H] mm/slab: make __free(kfree) accept error pointers

## Summary
Severity: High
Advisory: CVE-2024-36890
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36890
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.91, >=6.2.0 <6.6.31, >=6.5.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/slab: make __free(kfree) accept error pointers

Currently, if an automatically freed allocation is an error pointer that
will lead to a crash.  An example of this is in wm831x_gpio_dbg_show().

   171	char *label __free(kfree) = gpiochip_dup_line_label(chip, i);
   172	if (IS_ERR(label)) {
   173		dev_err(wm831x->dev, "Failed to duplicate label\n");
   174		continue;
   175  }

The auto clean up function should check for error pointers as well,
otherwise we're going to keep hitting issues like this.

## References
- https://git.kernel.org/stable/c/79cbe0be6c0317b215ddd8bd3e32f0afdac48543
- https://git.kernel.org/stable/c/946771c2a2b1150f9b7286feadc3aa1e15a1eb16
- https://git.kernel.org/stable/c/9f6eb0ab4f95240589ee85fd9886a944cd3645b2
- https://git.kernel.org/stable/c/ac6cf3ce9b7d12acb7b528248df5f87caa25fcdc
- https://git.kernel.org/stable/c/cd7eb8f83fcf258f71e293f7fc52a70be8ed0128
- https://git.kernel.org/stable/c/edca32f87329d6e341d2143a3b58ec254e8f6b88
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36890.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36890
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
