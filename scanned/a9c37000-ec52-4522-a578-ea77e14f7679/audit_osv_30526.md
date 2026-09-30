# [H] mm/mremap: fix address wraparound in move_page_tables()

## Summary
Severity: High
Advisory: CVE-2024-53111
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53111
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/mremap: fix address wraparound in move_page_tables()

On 32-bit platforms, it is possible for the expression `len + old_addr <
old_end` to be false-positive if `len + old_addr` wraps around. 
`old_addr` is the cursor in the old range up to which page table entries
have been moved; so if the operation succeeded, `old_addr` is the *end* of
the old region, and adding `len` to it can wrap.

The overflow causes mremap() to mistakenly believe that PTEs have been
copied; the consequence is that mremap() bails out, but doesn't move the
PTEs back before the new VMA is unmapped, causing anonymous pages in the
region to be lost.  So basically if userspace tries to mremap() a
private-anon region and hits this bug, mremap() will return an error and
the private-anon region's contents appear to have been zeroed.

The idea of this check is that `old_end - len` is the original start
address, and writing the check that way also makes it easier to read; so
fix the check by rearranging the comparison accordingly.

(An alternate fix would be to refactor this function by introducing an
"orig_old_start" variable or such.)


Tested in a VM with a 32-bit X86 kernel; without the patch:

```
user@horn:~/big_mremap$ cat test.c
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <err.h>
#include <sys/mman.h>

#define ADDR1 ((void*)0x60000000)
#define ADDR2 ((void*)0x10000000)
#define SIZE          0x50000000uL

int main(void) {
  unsigned char *p1 = mmap(ADDR1, SIZE, PROT_READ|PROT_WRITE,
      MAP_ANONYMOUS|MAP_PRIVATE|MAP_FIXED_NOREPLACE, -1, 0);
  if (p1 == MAP_FAILED)
    err(1, "mmap 1");
  unsigned char *p2 = mmap(ADDR2, SIZE, PROT_NONE,
      MAP_ANONYMOUS|MAP_PRIVATE|MAP_FIXED_NOREPLACE, -1, 0);
  if (p2 == MAP_FAILED)
    err(1, "mmap 2");
  *p1 = 0x41;
  printf("first char is 0x%02hhx\n", *p1);
  unsigned char *p3 = mremap(p1, SIZE, SIZE,
      MREMAP_MAYMOVE|MREMAP_FIXED, p2);
  if (p3 == MAP_FAILED) {
    printf("mremap() failed; first char is 0x%02hhx\n", *p1);
  } else {
    printf("mremap() succeeded; first char is 0x%02hhx\n", *p3);
  }
}
user@horn:~/big_mremap$ gcc -static -o test test.c
user@horn:~/big_mremap$ setarch -R ./test
first char is 0x41
mremap() failed; first char is 0x00
```

With the patch:

```
user@horn:~/big_mremap$ setarch -R ./test
first char is 0x41
mremap() succeeded; first char is 0x41
```

## References
- https://git.kernel.org/stable/c/909543dc279a91122fb08e4653a72b82f0ad28f4
- https://git.kernel.org/stable/c/a4a282daf1a190f03790bf163458ea3c8d28d217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53111.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
