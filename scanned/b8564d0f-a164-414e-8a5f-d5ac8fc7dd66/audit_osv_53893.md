# [M] CVE-2023-31084

## Summary
Severity: Medium
Advisory: CVE-2023-31084
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-31084
Type: osv

## Details
An issue was discovered in drivers/media/dvb-core/dvb_frontend.c in the Linux kernel 6.2. There is a blocking operation when a task is in !TASK_RUNNING. In dvb_frontend_get_event, wait_event_interruptible is called; the condition is dvb_frontend_test_event(fepriv,events). In dvb_frontend_test_event, down(&fepriv->sem) is called. However, wait_event_interruptible would put the process to sleep, and down(&fepriv->sem) may block the process.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6HIEOLEOURP4BJZMIL7UGGPYRRB44UDN/
- https://lore.kernel.org/all/CA+UBctCu7fXn4q41O_3=id1+OdyQ85tZY1x+TkT-6OVBL6KAUw%40mail.gmail.com/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b8c75e4a1b325ea0a9433fa8834be97b5836b946
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AOATNX5UFL7V7W2QDIQKOHFFHYKWFP4W/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20230929-0003/
- https://www.debian.org/security/2023/dsa-5448
- https://www.debian.org/security/2023/dsa-5480
