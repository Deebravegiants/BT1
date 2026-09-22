# [M] Integer overflow in the bundled Brotli C library

## Summary
Severity: Medium
Advisory: GHSA-5v8v-66v8-mwm7
CVE: CVE-2020-8927
CWE: CWE-120
Ecosystem: NuGet, PyPI, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5v8v-66v8-mwm7
Type: github-advisory

## Affected
- crates.io: `compu-brotli-sys` — affected >=0 <1.0.9
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=3.0.0 <3.1.23
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.osx-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.osx-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-musl-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.osx-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.browser-wasm` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=5.0.0 <5.0.15
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.linux-x64.Cross.android-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.linux-x64.Cross.android-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.linux-x64.Cross.android-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.linux-x64.Cross.android-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.linux-x64.Cross.browser-wasm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.android-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.android-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.android-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.android-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.browser-wasm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.ios-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.ios-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.iossimulator-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.iossimulator-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.iossimulator-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.maccatalyst-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.maccatalyst-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.tvos-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.tvossimulator-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.osx-x64.Cross.tvossimulator-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-arm.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-x64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.android-x86.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.browser-wasm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.AOT.win-x64.Cross.browser-wasm.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.linux-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.AOT.osx-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.linux-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.LLVM.osx-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x86.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x86.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.android-x86.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.browser-wasm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.browser-wasm.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.browser-wasm.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.browser-wasm.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.ios-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x86.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x86.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.iossimulator-x86.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-musl-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.linux-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-x64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-x64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.maccatalyst-x64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.osx-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.osx-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvos-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvos-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvos-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvos-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-arm64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-arm64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-arm64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-x64.Msi.arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-x64.Msi.x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.tvossimulator-x64.Msi.x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.win-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.Mono.win-x86` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-musl-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.linux-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.osx-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.osx-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-arm64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-x64` — affected >=6.0.0 <6.0.3
- NuGet: `Microsoft.NETCore.App.Runtime.win-x86` — affected >=6.0.0 <6.0.3
- PyPI: `brotli` — affected >=0 <1.0.8

## Details
A buffer overflow exists in the Brotli library versions prior to 1.0.8 where an attacker controlling the input length of a "one-shot" decompression request to a script can trigger a crash, which happens when copying over chunks of data larger than 2 GiB. It is recommended to update your Brotli library to 1.0.8 or later. If one cannot update, we recommend to use the "streaming" API as opposed to the "one-shot" API, and impose chunk size limits.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8927
- https://github.com/bitemyapp/brotli2-rs/issues/45
- https://github.com/github/advisory-database/issues/785
- https://github.com/google/brotli/commit/223d80cfbec8fd346e32906c732c8ede21f0cea6
- https://www.debian.org/security/2020/dsa-4801
- https://usn.ubuntu.com/4568-1
- https://rustsec.org/advisories/RUSTSEC-2021-0132.html
- https://rustsec.org/advisories/RUSTSEC-2021-0131.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZXEQ3GQVELA2T4HNZG7VPMS2HDVXMJRG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WW62OZEY2GHJL4JCOLJRBSRETXDHMWRK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/W23CUADGMVMQQNFKHPHXVP7RPZJZNN6I
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQLM7ABVCYJLF6JRPF3M3EBXW63GNC27
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MMBKACMLSRX7JJSKBTR35UOEP2WFR6QP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M4VCDOJGL6BK3HB4XRD2WETBPYX2ITF6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J4E265WKWKYMK2RYYSIXBEGZTDY5IQE6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4TOGTZ2ZWDH662ZNFFSZVL3M5AJXV6JF
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/356JOYTWW4BWSZ42SEFLV7NYHL3S3AEH
- https://lists.debian.org/debian-lts-announce/2020/12/msg00003.html
- https://github.com/pypa/advisory-database/tree/main/vulns/brotli/PYSEC-2020-29.yaml
- https://github.com/google/brotli/releases/tag/v1.0.9
