# [M] sock_map: fix a NULL pointer dereference in sock_map_link_update_prog()

## Summary
Severity: Medium
Advisory: CVE-2024-50260
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50260
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

sock_map: fix a NULL pointer dereference in sock_map_link_update_prog()

The following race condition could trigger a NULL pointer dereference:

sock_map_link_detach():		sock_map_link_update_prog():
   mutex_lock(&sockmap_mutex);
   ...
   sockmap_link->map = NULL;
   mutex_unlock(&sockmap_mutex);
   				   mutex_lock(&sockmap_mutex);
				   ...
				   sock_map_prog_link_lookup(sockmap_link->map);
				   mutex_unlock(&sockmap_mutex);
   <continue>

Fix it by adding a NULL pointer check. In this specific case, it makes
no sense to update a link which is being released.

## References
- https://git.kernel.org/stable/c/740be3b9a6d73336f8c7d540842d0831dc7a808b
- https://git.kernel.org/stable/c/9afe35fdda16e09d5bd3c49a68ba8c680dd678bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50260.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50260
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
