# [H] ASoC: mediatek: mt8195: Add platform entry for ETDM1_OUT_BE dai link

## Summary
Severity: High
Advisory: CVE-2024-42088
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42088
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: mt8195: Add platform entry for ETDM1_OUT_BE dai link

Commit e70b8dd26711 ("ASoC: mediatek: mt8195: Remove afe-dai component
and rework codec link") removed the codec entry for the ETDM1_OUT_BE
dai link entirely instead of replacing it with COMP_EMPTY(). This worked
by accident as the remaining COMP_EMPTY() platform entry became the codec
entry, and the platform entry became completely empty, effectively the
same as COMP_DUMMY() since snd_soc_fill_dummy_dai() doesn't do anything
for platform entries.

This causes a KASAN out-of-bounds warning in mtk_soundcard_common_probe()
in sound/soc/mediatek/common/mtk-soundcard-driver.c:

	for_each_card_prelinks(card, i, dai_link) {
		if (adsp_node && !strncmp(dai_link->name, "AFE_SOF", strlen("AFE_SOF")))
			dai_link->platforms->of_node = adsp_node;
		else if (!dai_link->platforms->name && !dai_link->platforms->of_node)
			dai_link->platforms->of_node = platform_node;
	}

where the code expects the platforms array to have space for at least one entry.

Add an COMP_EMPTY() entry so that dai_link->platforms has space.

## References
- https://git.kernel.org/stable/c/282a4482e198e03781c152c88aac8aa382ef9a55
- https://git.kernel.org/stable/c/42b9ab7a4d7e6c5efd71847541e4fcc213585aad
- https://git.kernel.org/stable/c/62f61129621ce7e05a6d24584660f79bf081b483
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42088.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
