# [H] wifi: iwlwifi: limit printed string from FW file

## Summary
Severity: High
Advisory: CVE-2025-21905
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21905
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: limit printed string from FW file

There's no guarantee here that the file is always with a
NUL-termination, so reading the string may read beyond the
end of the TLV. If that's the last TLV in the file, it can
perhaps even read beyond the end of the file buffer.

Fix that by limiting the print format to the size of the
buffer we have.

## References
- https://git.kernel.org/stable/c/38f0d398b6d7640d223db69df022c4a232f24774
- https://git.kernel.org/stable/c/47616b82f2d42ea2060334746fed9a2988d845c9
- https://git.kernel.org/stable/c/59cdda202829d1d6a095d233386870a59aff986f
- https://git.kernel.org/stable/c/88ed69f924638c7503644e1f8eed1e976f3ffa7a
- https://git.kernel.org/stable/c/b02f8d5a71c8571ccf77f285737c566db73ef5e5
- https://git.kernel.org/stable/c/c0e626f2b2390472afac52dfe72b29daf9ed8e1d
- https://git.kernel.org/stable/c/e0dc2c1bef722cbf16ae557690861e5f91208129
- https://git.kernel.org/stable/c/f265e6031d0bc4fc40c4619cb42466722b46eaa9
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21905.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21905
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
