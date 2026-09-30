# [H] nubus: Partially revert proc_create_single_data() conversion

## Summary
Severity: High
Advisory: CVE-2023-53217
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53217
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.188, >=5.11.0 <5.15.120, >=5.16.0 <6.1.38, >=6.2.0 <6.3.12, >=6.4.0 <6.4.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nubus: Partially revert proc_create_single_data() conversion

The conversion to proc_create_single_data() introduced a regression
whereby reading a file in /proc/bus/nubus results in a seg fault:

    # grep -r . /proc/bus/nubus/e/
    Data read fault at 0x00000020 in Super Data (pc=0x1074c2)
    BAD KERNEL BUSERR
    Oops: 00000000
    Modules linked in:
    PC: [<001074c2>] PDE_DATA+0xc/0x16
    SR: 2010  SP: 38284958  a2: 01152370
    d0: 00000001    d1: 01013000    d2: 01002790    d3: 00000000
    d4: 00000001    d5: 0008ce2e    a0: 00000000    a1: 00222a40
    Process grep (pid: 45, task=142f8727)
    Frame format=B ssw=074d isc=2008 isb=4e5e daddr=00000020 dobuf=01199e70
    baddr=001074c8 dibuf=ffffffff ver=f
    Stack from 01199e48:
	    01199e70 00222a58 01002790 00000000 011a3000 01199eb0 015000c0 00000000
	    00000000 01199ec0 01199ec0 000d551a 011a3000 00000001 00000000 00018000
	    d003f000 00000003 00000001 0002800d 01052840 01199fa8 c01f8000 00000000
	    00000029 0b532b80 00000000 00000000 00000029 0b532b80 01199ee4 00103640
	    011198c0 d003f000 00018000 01199fa8 00000000 011198c0 00000000 01199f4c
	    000b3344 011198c0 d003f000 00018000 01199fa8 00000000 00018000 011198c0
    Call Trace: [<00222a58>] nubus_proc_rsrc_show+0x18/0xa0
     [<000d551a>] seq_read+0xc4/0x510
     [<00018000>] fp_fcos+0x2/0x82
     [<0002800d>] __sys_setreuid+0x115/0x1c6
     [<00103640>] proc_reg_read+0x5c/0xb0
     [<00018000>] fp_fcos+0x2/0x82
     [<000b3344>] __vfs_read+0x2c/0x13c
     [<00018000>] fp_fcos+0x2/0x82
     [<00018000>] fp_fcos+0x2/0x82
     [<000b8aa2>] sys_statx+0x60/0x7e
     [<000b34b6>] vfs_read+0x62/0x12a
     [<00018000>] fp_fcos+0x2/0x82
     [<00018000>] fp_fcos+0x2/0x82
     [<000b39c2>] ksys_read+0x48/0xbe
     [<00018000>] fp_fcos+0x2/0x82
     [<000b3a4e>] sys_read+0x16/0x1a
     [<00018000>] fp_fcos+0x2/0x82
     [<00002b84>] syscall+0x8/0xc
     [<00018000>] fp_fcos+0x2/0x82
     [<0000c016>] not_ext+0xa/0x18
    Code: 4e5e 4e75 4e56 0000 206e 0008 2068 ffe8 <2068> 0020 2008 4e5e 4e75 4e56 0000 2f0b 206e 0008 2068 0004 2668 0020 206b ffe8
    Disabling lock debugging due to kernel taint

    Segmentation fault

The proc_create_single_data() conversion does not work because
single_open(file, nubus_proc_rsrc_show, PDE_DATA(inode)) is not
equivalent to the original code.

## References
- https://git.kernel.org/stable/c/0e96647cff9224db564a1cee6efccb13dbe11ee2
- https://git.kernel.org/stable/c/67e3b5230cefed1eca470c460a2035f02986cebb
- https://git.kernel.org/stable/c/9877533e1401dbbb2c7da8badda05d196aa07623
- https://git.kernel.org/stable/c/a03f2f4bd49030f57849227be9ba38a3eb1edb61
- https://git.kernel.org/stable/c/c06edf13f4cf7f9e8ff4bc6f7e951e4f074dc105
- https://git.kernel.org/stable/c/f70407e8e0272e00d133c5e039168ff1bae6bcac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53217.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53217
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
