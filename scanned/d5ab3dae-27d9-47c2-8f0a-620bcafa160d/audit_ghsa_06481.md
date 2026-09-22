# [M] vLLM: Processing differential in multi-channel audio downmixing enables hidden-input/moderation bypass for audio models

## Summary
Severity: Medium
Advisory: GHSA-6c4r-fmh3-7rh8
CVE: CVE-2026-34760
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-6c4r-fmh3-7rh8
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.5.5 <0.18.0

## Details
## Issue Description
Librosa defaults to using `numpy.mean` for mono downmixing (`to_mono`), while the international standard ITU-R BS.775-4 specifies a weighted downmixing algorithm. This discrepancy results in:
- Inconsistency between audio heard by humans (e.g., through headphones/regular speakers) and audio processed by AI models (Which infra via Librosa, such as vllm, transformer).

https://github.com/librosa/librosa/blob/af8c839fb15317fa2712ea66e7a22da6a9267b32/librosa/core/audio.py#L478
## Attack Scenario and Impact

### LFE (Low-Frequency Effects) Channel Exploit
Attackers can craft special multichannel audio files containing:
1. Normal content in front channels (L/R)
2. Either interference signals or hidden content in the LFE channel

**Notice:** It is worth noting that not only the LFE channel is excluded, but in fact, channels beyond the 6th (such as rear surround channels, overhead channels, height speakers, etc.) are also not supported.

**Attack Methodology:**

Attackers can create specially engineered multichannel audio with LFE interference, where front channels (L/R) contain normal content while the LFE channel carries interference signals or hidden content. When played on consumer devices that ignore LFE channels, only the normal content is heard. However, when processed by AI systems using Librosa (which mixes all channels), the LFE interference affects speech recognition feature extraction or masks critical detection features. This enables malicious content to bypass AI detection while still reaching end users, potentially compromising voice authentication systems, evading content moderation, or disrupting speech recognition accuracy.

**Potential Exploitation Scenarios:**
- Voice authentication systems may be tricked into accepting anomalous audio
- Content moderation systems may fail to detect prohibited content hidden in LFE channels 
- Speech recognition systems may produce incorrect transcriptions

**Note:** `torch.audio` implements this correctly. Failure to do so may lead to inconsistencies between training and test audio, resulting in performance degradation.


## Resources

- [ITU-R BS.775-4 Standard](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.775-4-202212-I!!PDF-E.pdf)
- [Librosa Source Code](https://github.com/librosa/librosa/blob/af8c839fb15317fa2712ea66e7a22da6a9267b32/librosa/core/audio.py#L478)
- [Librosa securty report](https://github.com/librosa/librosa/security/advisories/GHSA-vfm7-86xr-5mrh)

## Fixes

- https://github.com/vllm-project/vllm/pull/37058, which removes the librosa dependency from vLLM.

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-6c4r-fmh3-7rh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34760
- https://github.com/vllm-project/vllm/pull/37058
- https://github.com/vllm-project/vllm/commit/c7f98b4d0a63b32ed939e2b6dfaa8a626e9b46c4
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2299.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/releases/tag/v0.18.0
