# [H] bpf: fix recursive lock when verdict program return SK_PASS

## Summary
Severity: High
Advisory: CVE-2024-56694
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56694
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.233, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.9.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: fix recursive lock when verdict program return SK_PASS

When the stream_verdict program returns SK_PASS, it places the received skb
into its own receive queue, but a recursive lock eventually occurs, leading
to an operating system deadlock. This issue has been present since v6.9.

'''
sk_psock_strp_data_ready
    write_lock_bh(&sk->sk_callback_lock)
    strp_data_ready
      strp_read_sock
        read_sock -> tcp_read_sock
          strp_recv
            cb.rcv_msg -> sk_psock_strp_read
              # now stream_verdict return SK_PASS without peer sock assign
              __SK_PASS = sk_psock_map_verd(SK_PASS, NULL)
              sk_psock_verdict_apply
                sk_psock_skb_ingress_self
                  sk_psock_skb_ingress_enqueue
                    sk_psock_data_ready
                      read_lock_bh(&sk->sk_callback_lock) <= dead lock

'''

This topic has been discussed before, but it has not been fixed.
Previous discussion:
https://lore.kernel.org/all/6684a5864ec86_403d20898@john.notmuch

## References
- https://git.kernel.org/stable/c/01f1b88acfd79103da0610b45471f6c88ea98d72
- https://git.kernel.org/stable/c/221109ba2127eabd0aa64718543638b58b15df56
- https://git.kernel.org/stable/c/386efa339e08563dd33e83bc951aea5d407fe578
- https://git.kernel.org/stable/c/6694f7acd625ed854bf6342926e771d65dad7f69
- https://git.kernel.org/stable/c/8ca2a1eeadf09862190b2810697702d803ceef2d
- https://git.kernel.org/stable/c/da2bc8a0c8f3ac66fdf980fc59936f851a083561
- https://git.kernel.org/stable/c/f84c5ef6ca23cc2f72f3b830d74f67944684bb05
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56694.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56694
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
