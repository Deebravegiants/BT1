# [M] CVE-2021-47650

## Summary
Severity: Medium
Advisory: CVE-2021-47650
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47650
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: soc-compress: prevent the potentially use of null pointer

There is one call trace that snd_soc_register_card()
->snd_soc_bind_card()->soc_init_pcm_runtime()
->snd_soc_dai_compress_new()->snd_soc_new_compress().
In the trace the 'codec_dai' transfers from card->dai_link,
and we can see from the snd_soc_add_pcm_runtime() in
snd_soc_bind_card() that, if value of card->dai_link->num_codecs
is 0, then 'codec_dai' could be null pointer caused
by index out of bound in 'asoc_rtd_to_codec(rtd, 0)'.
And snd_soc_register_card() is called by various platforms.
Therefore, it is better to add the check in the case of misusing.
And because 'cpu_dai' has already checked in soc_init_pcm_runtime(),
there is no need to check again.
Adding the check as follow, then if 'codec_dai' is null,
snd_soc_new_compress() will not pass through the check
'if (playback + capture != 1)', avoiding the leftover use of
'codec_dai'.

## References
- https://git.kernel.org/stable/c/68a69ad8df959e5211ed4a8e120783b2d352ea74
- https://git.kernel.org/stable/c/de2c6f98817fa5decb9b7d3b3a8a3ab864c10588
- https://git.kernel.org/stable/c/f69a75cb8a98c6c487d620442c68595726a69f60
- https://git.kernel.org/stable/c/fc237b8d624f4bcb0f21a532627ce4e3b3a85569
- https://git.kernel.org/stable/c/08af6da684b44097ea09f1d74d5858b837ed203b
- https://git.kernel.org/stable/c/4639c1d97f385f4784f44d66a3da0672f4951ada
