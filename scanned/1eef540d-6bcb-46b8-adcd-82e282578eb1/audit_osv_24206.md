# [M] parisc: led: Fix potential null-ptr-deref in start_task()

## Summary
Severity: Medium
Advisory: CVE-2022-50415
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50415
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

parisc: led: Fix potential null-ptr-deref in start_task()

start_task() calls create_singlethread_workqueue() and not checked the
ret value, which may return NULL. And a null-ptr-deref may happen:

start_task()
    create_singlethread_workqueue() # failed, led_wq is NULL
    queue_delayed_work()
        queue_delayed_work_on()
            __queue_delayed_work()  # warning here, but continue
                __queue_work()      # access wq->flags, null-ptr-deref

Check the ret value and return -ENOMEM if it is NULL.

## References
- https://git.kernel.org/stable/c/3505c187b86136250b39e62c72a3a70435277af6
- https://git.kernel.org/stable/c/41f563ab3c33698bdfc3403c7c2e6c94e73681e4
- https://git.kernel.org/stable/c/5e4500454d75dd249be4695d83afa3ba0724c37e
- https://git.kernel.org/stable/c/67c98fec87ed76b1feb2ae810051afd88dfa9df6
- https://git.kernel.org/stable/c/77f8b628affaec692d83ad8bfa3520db8a0cc493
- https://git.kernel.org/stable/c/ac838c663ba1fd6bff35a817fd89a47ab55e88e0
- https://git.kernel.org/stable/c/c6db0c32f39684c89c97bc1ba1c9c4249ca09e48
- https://git.kernel.org/stable/c/fc307b2905a3dd75c50a53b4d87ac9c912fb7c4e
- https://git.kernel.org/stable/c/fc6d0f65f22040c6cc8a5ce032bf90252629de50
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50415.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50415
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
