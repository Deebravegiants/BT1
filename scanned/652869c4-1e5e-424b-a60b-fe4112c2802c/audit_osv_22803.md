# [M] Git subject to exposure of sensitive information via local clone of symbolic links

## Summary
Severity: Medium
Advisory: CVE-2022-39253
Aliases: GHSA-3wp6-j8xr-qw85
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-39253
Type: osv

## Details
Git is an open source, scalable, distributed revision control system. Versions prior to 2.30.6, 2.31.5, 2.32.4, 2.33.5, 2.34.5, 2.35.5, 2.36.3, and 2.37.4 are subject to exposure of sensitive information to a malicious actor. When performing a local clone (where the source and target of the clone are on the same volume), Git copies the contents of the source's `$GIT_DIR/objects` directory into the destination by either creating hardlinks to the source contents, or copying them (if hardlinks are disabled via `--no-hardlinks`). A malicious actor could convince a victim to clone a repository with a symbolic link pointing at sensitive information on the victim's machine. This can be done either by having the victim clone a malicious repository on the same machine, or having them clone a malicious repository embedded as a bare repository via a submodule from any source, provided they clone with the `--recurse-submodules` option. Git does not create symbolic links in the `$GIT_DIR/objects` directory. The problem has been patched in the versions published on 2022-10-18, and backported to v2.30.x. Potential workarounds: Avoid cloning untrusted repositories using the `--local` optimization when on a shared machine, either by passing the `--no-local` option to `git clone` or cloning from a URL that uses the `file://` scheme. Alternatively, avoid cloning repositories from untrusted sources with `--recurse-submodules` or run `git config --global protocol.file.allow user`.

## References
- https://support.apple.com/kb/HT213496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39253.json
- https://github.com/git/git/security/advisories/GHSA-3wp6-j8xr-qw85
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7B6JPKX5CGGLAHXJVQMIZNNEEB72FHD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JMQWGMDLX6KTVWW5JZLVPI7ICAK72TN7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OHNO2FB55CPX47BAXMBWUBGWHO6N6ZZH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UKFHE4KVD7EKS5J3KTDFVBEKU3CLXGVV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VFYXCTLOSESYIP72BUYD6ECDIMUM4WMB/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39253
- https://security.gentoo.org/glsa/202312-15
- http://seclists.org/fulldisclosure/2022/Nov/1
- http://www.openwall.com/lists/oss-security/2023/02/14/5
- http://www.openwall.com/lists/oss-security/2024/05/14/2
- https://lists.debian.org/debian-lts-announce/2022/12/msg00025.html
