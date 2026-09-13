# [H] ALSA: sh: aica: reorder cleanup operations to avoid UAF bugs

## Summary
Severity: High
Advisory: CVE-2024-26654
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-01
Source: https://osv.dev/vulnerability/CVE-2024-26654
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: sh: aica: reorder cleanup operations to avoid UAF bugs

The dreamcastcard->timer could schedule the spu_dma_work and the
spu_dma_work could also arm the dreamcastcard->timer.

When the snd_pcm_substream is closing, the aica_channel will be
deallocated. But it could still be dereferenced in the worker
thread. The reason is that del_timer() will return directly
regardless of whether the timer handler is running or not and
the worker could be rescheduled in the timer handler. As a result,
the UAF bug will happen. The racy situation is shown below:

      (Thread 1)                 |      (Thread 2)
snd_aicapcm_pcm_close()          |
 ...                             |  run_spu_dma() //worker
                                 |    mod_timer()
  flush_work()                   |
  del_timer()                    |  aica_period_elapsed() //timer
  kfree(dreamcastcard->channel)  |    schedule_work()
                                 |  run_spu_dma() //worker
  ...                            |    dreamcastcard->channel-> //USE

In order to mitigate this bug and other possible corner cases,
call mod_timer() conditionally in run_spu_dma(), then implement
PCM sync_stop op to cancel both the timer and worker. The sync_stop
op will be called from PCM core appropriately when needed.

## References
- https://git.kernel.org/stable/c/051e0840ffa8ab25554d6b14b62c9ab9e4901457
- https://git.kernel.org/stable/c/3c907bf56905de7d27b329afaf59c2fb35d17b04
- https://git.kernel.org/stable/c/4206ad65a0ee76920041a755bd3c17c6ba59bba2
- https://git.kernel.org/stable/c/61d4787692c1fccdc268ffa7a891f9c149f50901
- https://git.kernel.org/stable/c/8c990221681688da34295d6d76cc2f5b963e83f5
- https://git.kernel.org/stable/c/9d66ae0e7bb78b54e1e0525456c6b54e1d132046
- https://git.kernel.org/stable/c/aa39e6878f61f50892ee2dd9d2176f72020be845
- https://git.kernel.org/stable/c/e955e8a7f38a856fc6534ba4e6bffd4d5cc80ac3
- https://git.kernel.org/stable/c/eeb2a2ca0b8de7e1c66afaf719529154e7dc60b2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26654.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26654
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
