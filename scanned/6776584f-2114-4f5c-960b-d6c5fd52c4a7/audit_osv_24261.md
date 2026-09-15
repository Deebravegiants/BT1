# [H] staging: media: tegra-video: fix device_node use after free

## Summary
Severity: High
Advisory: CVE-2022-50745
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50745
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: media: tegra-video: fix device_node use after free

At probe time this code path is followed:

 * tegra_csi_init
   * tegra_csi_channels_alloc
     * for_each_child_of_node(node, channel) -- iterates over channels
       * automatically gets 'channel'
         * tegra_csi_channel_alloc()
           * saves into chan->of_node a pointer to the channel OF node
       * automatically gets and puts 'channel'
       * now the node saved in chan->of_node has refcount 0, can disappear
   * tegra_csi_channels_init
     * iterates over channels
       * tegra_csi_channel_init -- uses chan->of_node

After that, chan->of_node keeps storing the node until the device is
removed.

of_node_get() the node and of_node_put() it during teardown to avoid any
risk.

## References
- https://git.kernel.org/stable/c/0fd003d3c708c80350a815eaf37b8e1114b976cf
- https://git.kernel.org/stable/c/5451efb2ca30f3c42b9efb8327ce35b62870dbd3
- https://git.kernel.org/stable/c/6512c9498fcb97e7c760e3ef86b2272f2c0f765f
- https://git.kernel.org/stable/c/c4d344163c3a7f90712525f931a6c016bbb35e18
- https://git.kernel.org/stable/c/ce50c612458091d926ccb05d7db11d9f93532db2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50745.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50745
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
